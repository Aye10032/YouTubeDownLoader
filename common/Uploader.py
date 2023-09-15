import asyncio
import base64
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from dataclasses import asdict, dataclass, field, InitVar
from functools import reduce
from json import JSONDecodeError
from os.path import splitext, basename
from pathlib import Path
from typing import Union, Any
from urllib import parse
from urllib.parse import quote
from aiohttp import ClientError, ClientSession

import requests.utils
import rsa
import xml.etree.ElementTree as ET

from requests.adapters import HTTPAdapter, Retry

from common.SignalBus import signal_bus


class UploadBase:
    def __init__(self, principal, data, persistence_path=None, postprocessor=None):
        self.principal = principal
        self.persistence_path = persistence_path
        self.data = data
        self.post_processor = postprocessor

    # @property
    @staticmethod
    def file_list(index):
        file_list = []
        for file_name in os.listdir('.'):
            if index in file_name and os.path.isfile(file_name):
                file_list.append(file_name)
        file_list = sorted(file_list)
        return file_list

    @staticmethod
    def remove_filelist(file_list):
        for r in file_list:
            os.remove(r)
            print('[info] 删除-' + r)

    def filter_file(self, index):
        media_extensions = ['.mp4', '.flv', '.ts']
        file_list = UploadBase.file_list(index)
        if len(file_list) == 0:
            return False
        for f in file_list:
            if f.endswith('.part'):
                new_name = os.path.splitext(f)[0]
                shutil.move(f, new_name)
                print(f'[info] {f}存在已更名为{new_name}')
        for r in file_list:
            name, ext = os.path.splitext(r)
            if ext in ('.mp4', '.flv', '.ts'):
                file_size = os.path.getsize(r) / 1024 / 1024
                threshold = self.data.get('threshold', 2)
                if file_size <= threshold:
                    self.remove_file(r)
                    print(f'[info] 过滤删除-{r}')
            if ext == '.xml':  # 过滤不存在对应视频的xml弹幕文件
                xml_file_name = name
                media_regex = re.compile(r'^{}(\.(mp4|flv|ts))?$'.format(
                    re.escape(xml_file_name)
                ))
                if not any(media_regex.match(f'{xml_file_name}{ext2}') for ext2 in media_extensions for x in file_list):
                    self.remove_file(r)
                    print(f'无视频，已过滤删除-{r}')
        file_list = UploadBase.file_list(index)
        if len(file_list) == 0:
            print('[info] 视频过滤后无文件可传')
            return False

        return True

    def remove_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8'):
            os.remove(file_path)

    def upload(self, file_list):
        raise NotImplementedError()

    def start(self):
        if self.filter_file(self.principal):
            print('[info] 准备上传' + self.data["format_title"])
            needed2process = self.upload(UploadBase.file_list(self.principal))
            if needed2process:
                self.postprocessor(needed2process)

    def postprocessor(self, data):
        # data = file_list
        if self.post_processor is None:
            return self.remove_filelist(data)
        for post_processor in self.post_processor:
            if post_processor == 'rm':
                self.remove_filelist(data)
                continue
            if post_processor.get('mv'):
                for file in data:
                    path = Path(file)
                    dest = Path(post_processor['mv'])
                    if not dest.is_dir():
                        dest.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(path, dest / path.name)
                    except Exception as e:
                        print(e)
                        continue
                    print(f"[info] move to {(dest / path.name).absolute()}")
            if post_processor.get('run'):
                try:
                    process_output = subprocess.check_output(
                        post_processor['run'], shell=True,
                        input=reduce(lambda x, y: x + str(Path(y).absolute()) + '\n', data, ''),
                        stderr=subprocess.STDOUT, text=True)
                    print(f'[info] {process_output.rstrip()}')
                except subprocess.CalledProcessError as e:
                    print(f'[error] {e.output}')
                    continue


class BiliBili:
    def __init__(self, video: 'Data'):
        self.app_key = None
        self.appsec = None
        if self.app_key is None or self.appsec is None:
            self.app_key = 'ae57252b0c09105d'
            self.appsec = 'c75875c596a69eb55bd119e74b07cfe3'
        self.__session = requests.Session()
        self.video = video
        self.__session.mount('https://', HTTPAdapter(max_retries=Retry(total=5)))
        self.__session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108",
            "Referer": "https://www.bilibili.com/", 'Connection': 'keep-alive'
        })
        self.cookies = None
        self.access_token = None
        self.refresh_token = None
        self.account = None
        self.__bili_jct = None
        self._auto_os = None
        self.persistence_path = 'engine/bili.cookie'

    def check_tag(self, tag):
        r = self.__session.get("https://member.bilibili.com/x/vupre/web/topic/tag/check?tag=" + tag).json()
        if r["code"] == 0:
            return True
        else:
            return False

    def get_qrcode(self):
        params = {
            "appkey": "4409e2ce8ffd12b8",
            "local_id": "0",
            "ts": int(time.time()),
        }
        params["sign"] = hashlib.md5(
            f"{urllib.parse.urlencode(params)}59b43e04ad6965f34319062b478f83dd".encode()).hexdigest()
        response = self.__session.post("http://passport.bilibili.com/x/passport-tv-login/qrcode/auth_code", data=params,
                                       timeout=5)
        r = response.json()
        if r and r["code"] == 0:
            return r

    async def login_by_qrcode(self, value):
        params = {
            "appkey": "4409e2ce8ffd12b8",
            "auth_code": value["data"]["auth_code"],
            "local_id": "0",
            "ts": int(time.time()),
        }
        params["sign"] = hashlib.md5(
            f"{urllib.parse.urlencode(params)}59b43e04ad6965f34319062b478f83dd".encode()).hexdigest()
        for i in range(0, 120):
            await asyncio.sleep(1)
            response = self.__session.post("http://passport.bilibili.com/x/passport-tv-login/qrcode/poll", data=params,
                                           timeout=5)
            r = response.json()
            if r and r["code"] == 0:
                return r
        raise "Qrcode timeout"

    def tid_archive(self, cookies):
        requests.utils.add_dict_to_cookiejar(self.__session.cookies, cookies)
        response = self.__session.get("https://member.bilibili.com/x/vupre/web/archive/pre")
        return response.json()

    def login(self, persistence_path, user):
        self.persistence_path = persistence_path
        if os.path.isfile(persistence_path):
            print('使用持久化内容上传')
            signal_bus.log_signal.emit('使用持久化内容上传')
            self.load()
        if user.get('cookies'):
            self.cookies = user['cookies']
        if user.get('access_token'):
            self.access_token = user['access_token']
        if user.get('account'):
            self.account = user['account']
        if self.cookies:
            try:
                self.login_by_cookies(self.cookies)
            except:
                print('[error] login error')
                signal_bus.log_signal.emit('[error] login error')
                self.login_by_password(**self.account)
        else:
            self.login_by_password(**self.account)
        self.store()

    def load(self):
        try:
            with open(self.persistence_path) as f:
                self.cookies = json.load(f)
                self.access_token = self.cookies['access_token']
        except (JSONDecodeError, KeyError):
            print('[error] 加载cookie出错')

    def store(self):
        with open(self.persistence_path, "w") as f:
            json.dump({**self.cookies,
                       'access_token': self.access_token,
                       'refresh_token': self.refresh_token
                       }, f)

    def send_sms(self, phone_number, country_code):
        params = {
            "actionKey": "appkey",
            "appkey": "783bbb7264451d82",
            "build": 6510400,
            "channel": "bili",
            "cid": country_code,
            "device": "phone",
            "mobi_app": "android",
            "platform": "android",
            "tel": phone_number,
            "ts": int(time.time()),
        }
        sign = hashlib.md5(f"{urllib.parse.urlencode(params)}2653583c8873dea268ab9386918b1d65".encode()).hexdigest()
        payload = f"{urllib.parse.urlencode(params)}&sign={sign}"
        response = self.__session.post("https://passport.bilibili.com/x/passport-login/sms/send", data=payload,
                                       timeout=5)
        return response.json()

    def login_by_sms(self, code, params):
        params["code"] = code
        params["sign"] = hashlib.md5(
            f"{urllib.parse.urlencode(params)}59b43e04ad6965f34319062b478f83dd".encode()).hexdigest()
        response = self.__session.post("https://passport.bilibili.com/x/passport-login/login/sms", data=params,
                                       timeout=5)
        r = response.json()
        if r and r["code"] == 0:
            return r

    def login_by_password(self, username, password):
        print('使用账号上传')
        key_hash, pub_key = self.get_key()
        encrypt_password = base64.b64encode(rsa.encrypt(f'{key_hash}{password}'.encode(), pub_key))
        payload = {
            "actionKey": 'appkey',
            "appkey": self.app_key,
            "build": 6270200,
            "captcha": '',
            "challenge": '',
            "channel": 'bili',
            "device": 'phone',
            "mobi_app": 'android',
            "password": encrypt_password,
            "permission": 'ALL',
            "platform": 'android',
            "seccode": "",
            "subid": 1,
            "ts": int(time.time()),
            "username": username,
            "validate": "",
        }
        response = self.__session.post("https://passport.bilibili.com/x/passport-login/oauth2/login", timeout=5,
                                       data={**payload, 'sign': self.sign(parse.urlencode(payload))})
        r = response.json()
        if r['code'] != 0 or r.get('data') is None or r['data'].get('cookie_info') is None:
            raise RuntimeError(r)
        try:
            for cookie in r['data']['cookie_info']['cookies']:
                self.__session.cookies.set(cookie['name'], cookie['value'])
                if 'bili_jct' == cookie['name']:
                    self.__bili_jct = cookie['value']
            self.cookies = self.__session.cookies.get_dict()
            self.access_token = r['data']['token_info']['access_token']
            self.refresh_token = r['data']['token_info']['refresh_token']
        except:
            raise RuntimeError(r)
        return r

    def login_by_cookies(self, cookie):
        print('使用cookies上传')
        requests.utils.add_dict_to_cookiejar(self.__session.cookies, cookie)
        if 'bili_jct' in cookie:
            self.__bili_jct = cookie["bili_jct"]
        data = self.__session.get("https://api.bilibili.com/x/web-interface/nav", timeout=5).json()
        if data["code"] != 0:
            raise Exception(data)

    def sign(self, param):
        return hashlib.md5(f"{param}{self.appsec}".encode()).hexdigest()

    def get_key(self):
        url = "https://passport.bilibili.com/x/passport-login/web/key"
        payload = {
            'appkey': f'{self.app_key}',
            'sign': self.sign(f"appkey={self.app_key}"),
        }
        response = self.__session.get(url, data=payload, timeout=5)
        r = response.json()
        if r and r["code"] == 0:
            return r['data']['hash'], rsa.PublicKey.load_pkcs1_openssl_pem(r['data']['key'].encode())

    def probe(self):
        ret = self.__session.get('https://member.bilibili.com/preupload?r=probe', timeout=5).json()
        print(f"[info] 线路:{ret['lines']}")
        data, auto_os = None, None
        min_cost = 0
        if ret['probe'].get('get'):
            method = 'get'
        else:
            method = 'post'
            data = bytes(int(1024 * 0.1 * 1024))
        for line in ret['lines']:
            start = time.perf_counter()
            test = self.__session.request(method, f"https:{line['probe_url']}", data=data, timeout=30)
            cost = time.perf_counter() - start
            print(line['query'], cost)
            if test.status_code != 200:
                return
            if not min_cost or min_cost > cost:
                auto_os = line
                min_cost = cost
        auto_os['cost'] = min_cost
        return auto_os

    def upload_file(self, filepath: str, part_name: str, lines='AUTO', tasks=3):
        """上传本地视频文件,返回视频信息dict
        b站目前支持4种上传线路upos, kodo, gcs, bos
        gcs: {"os":"gcs","query":"bucket=bvcupcdngcsus&probe_version=20221109",
        "probe_url":"//storage.googleapis.com/bvcupcdngcsus/OK"},
        bos: {"os":"bos","query":"bucket=bvcupcdnboshb&probe_version=20221109",
        "probe_url":"??"}
        """
        preferred_upos_cdn = None
        if not self._auto_os:
            if lines == 'kodo':
                self._auto_os = {"os": "kodo", "query": "bucket=bvcupcdnkodobm&probe_version=20221109",
                                 "probe_url": "//up-na0.qbox.me/crossdomain.xml"}
            elif lines == 'bda2':
                self._auto_os = {"os": "upos", "query": "upcdn=bda2&probe_version=20221109",
                                 "probe_url": "//upos-sz-upcdnbda2.bilivideo.com/OK"}
                preferred_upos_cdn = 'bda2'
            elif lines == 'cs-bda2':
                self._auto_os = {"os": "upos", "query": "upcdn=bda2&probe_version=20221109",
                                 "probe_url": "//upos-cs-upcdnbda2.bilivideo.com/OK"}
                preferred_upos_cdn = 'bda2'
            elif lines == 'ws':
                self._auto_os = {"os": "upos", "query": "upcdn=ws&probe_version=20221109",
                                 "probe_url": "//upos-sz-upcdnws.bilivideo.com/OK"}
                preferred_upos_cdn = 'ws'
            elif lines == 'qn':
                self._auto_os = {"os": "upos", "query": "upcdn=qn&probe_version=20221109",
                                 "probe_url": "//upos-sz-upcdnqn.bilivideo.com/OK"}
                preferred_upos_cdn = 'qn'
            elif lines == 'cs-qn':
                self._auto_os = {"os": "upos", "query": "upcdn=qn&probe_version=20221109",
                                 "probe_url": "//upos-cs-upcdnqn.bilivideo.com/OK"}
                preferred_upos_cdn = 'qn'
            elif lines == 'cos':
                self._auto_os = {"os": "cos", "query": "",
                                 "probe_url": ""}
            elif lines == 'cos-internal':
                self._auto_os = {"os": "cos-internal", "query": "",
                                 "probe_url": ""}
            else:
                self._auto_os = self.probe()
            print(
                f"[info] 线路选择 => {self._auto_os['os']}: {self._auto_os['query']}. time: {self._auto_os.get('cost')}")
        if self._auto_os['os'] == 'upos':
            upload = self.upos
        elif self._auto_os['os'] == 'cos':
            upload = self.cos
        elif self._auto_os['os'] == 'cos-internal':
            upload = lambda *args, **kwargs: self.cos(*args, **kwargs, internal=True)
        elif self._auto_os['os'] == 'kodo':
            upload = self.kodo
        else:
            print(f"[error] NoSearch:{self._auto_os['os']}")
            signal_bus.log_signal.emit(f"[error] NoSearch:{self._auto_os['os']}")
            raise NotImplementedError(self._auto_os['os'])
        print(f"[info] os: {self._auto_os['os']}")
        signal_bus.log_signal.emit(f"[info] os: {self._auto_os['os']}")
        total_size = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            query = {
                'r': self._auto_os['os'] if self._auto_os['os'] != 'cos-internal' else 'cos',
                'profile': 'ugcupos/bup' if 'upos' == self._auto_os['os'] else "ugcupos/bupfetch",
                'ssl': 0,
                'version': '2.8.12',
                'build': 2081200,
                'name': part_name,
                'size': total_size,
            }
            resp = self.__session.get(
                f"https://member.bilibili.com/preupload?{self._auto_os['query']}", params=query,
                timeout=5)
            ret = resp.json()
            print(f"preupload: {ret}")
            if preferred_upos_cdn:
                original_endpoint: str = ret['endpoint']
                if re.match(r'//upos-(sz|cs)-upcdn(bda2|ws|qn)\.bilivideo\.com', original_endpoint):
                    if re.match(r'bda2|qn|ws', preferred_upos_cdn):
                        print(f"[debug] Preferred UpOS CDN: {preferred_upos_cdn}")
                        new_endpoint = re.sub(r'upcdn(bda2|qn|ws)', f'upcdn{preferred_upos_cdn}', original_endpoint)
                        print(f"[debug] {original_endpoint} => {new_endpoint}")
                        ret['endpoint'] = new_endpoint
                    else:
                        print(f"Unrecognized preferred_upos_cdn: {preferred_upos_cdn}")
                else:
                    print(
                        f"Assigned UpOS endpoint {original_endpoint} was never seen before, something else might have changed, so will not modify it")
            return asyncio.run(upload(f, total_size, ret, tasks=tasks))

    async def cos(self, file, name, total_size, ret, chunk_size=10485760, tasks=3, internal=False):
        filename = name
        url = ret["url"]
        if internal:
            url = url.replace("cos.accelerate", "cos-internal.ap-shanghai")
        biz_id = ret["biz_id"]
        post_headers = {
            "Authorization": ret["post_auth"],
        }
        put_headers = {
            "Authorization": ret["put_auth"],
        }

        initiate_multipart_upload_result = ET.fromstring(self.__session.post(f'{url}?uploads&output=json', timeout=5,
                                                                             headers=post_headers).content)
        upload_id = initiate_multipart_upload_result.find('UploadId').text
        # 开始上传
        parts = []  # 分块信息
        chunks = math.ceil(total_size / chunk_size)  # 获取分块数量

        async def upload_chunk(session, chunks_data, params):
            async with session.put(url, params=params, raise_for_status=True,
                                   data=chunks_data, headers=put_headers) as r:
                end = time.perf_counter() - start
                parts.append({"Part": {"PartNumber": params['chunk'] + 1, "ETag": r.headers['Etag']}})
                sys.stdout.write(f"\r{params['end'] / 1000 / 1000 / end:.2f}MB/s "
                                 f"=> {params['partNumber'] / chunks:.1%}")

        start = time.perf_counter()
        await self._upload({
            'uploadId': upload_id,
            'chunks': chunks,
            'total': total_size
        }, file, chunk_size, upload_chunk, tasks=tasks)
        cost = time.perf_counter() - start
        fetch_headers = {
            "X-Upos-Fetch-Source": ret["fetch_headers"]["X-Upos-Fetch-Source"],
            "X-Upos-Auth": ret["fetch_headers"]["X-Upos-Auth"],
            "Fetch-Header-Authorization": ret["fetch_headers"]["Fetch-Header-Authorization"]
        }
        parts = sorted(parts, key=lambda x: x['Part']['PartNumber'])
        complete_multipart_upload = ET.Element('CompleteMultipartUpload')
        for part in parts:
            part_et = ET.SubElement(complete_multipart_upload, 'Part')
            part_number = ET.SubElement(part_et, 'PartNumber')
            part_number.text = str(part['Part']['PartNumber'])
            e_tag = ET.SubElement(part_et, 'ETag')
            e_tag.text = part['Part']['ETag']
        xml = ET.tostring(complete_multipart_upload)
        ii = 0
        while ii <= 3:
            try:
                res = self.__session.post(url, params={'uploadId': upload_id}, data=xml, headers=post_headers,
                                          timeout=15)
                if res.status_code == 200:
                    break
                raise IOError(res.text)
            except IOError:
                ii += 1
                print("[info] 请求合并分片出现问题，尝试重连，次数：" + str(ii))
                signal_bus.log_signal.emit("[info] 请求合并分片出现问题，尝试重连，次数：" + str(ii))
                time.sleep(15)
        ii = 0
        while ii <= 3:
            try:
                res = self.__session.post("https:" + ret["fetch_url"], headers=fetch_headers, timeout=15).json()
                if res.get('OK') == 1:
                    print(f'[info] {filename} uploaded >> {total_size / 1000 / 1000 / cost:.2f}MB/s. {res}')
                    signal_bus.log_signal.emit(
                        f'[info] {filename} uploaded >> {total_size / 1000 / 1000 / cost:.2f}MB/s. {res}')
                    return {"title": splitext(filename)[0], "filename": ret["bili_filename"], "desc": ""}
                raise IOError(res)
            except IOError:
                ii += 1
                print("[info] 上传出现问题，尝试重连，次数：" + str(ii))
                signal_bus.log_signal.emit("[info] 上传出现问题，尝试重连，次数：" + str(ii))
                time.sleep(15)

    async def kodo(self, file, name, total_size, ret, chunk_size=4194304, tasks=3):
        filename = name
        bili_filename = ret['bili_filename']
        key = ret['key']
        endpoint = f"https:{ret['endpoint']}"
        token = ret['uptoken']
        fetch_url = ret['fetch_url']
        fetch_headers = ret['fetch_headers']
        url = f'{endpoint}/mkblk'
        headers = {
            'Authorization': f"UpToken {token}",
        }
        # 开始上传
        parts = []  # 分块信息
        chunks = math.ceil(total_size / chunk_size)  # 获取分块数量

        async def upload_chunk(session, chunks_data, params):
            async with session.post(f'{url}/{len(chunks_data)}',
                                    data=chunks_data, headers=headers) as response:
                end = time.perf_counter() - start
                ctx = await response.json()
                parts.append({"index": params['chunk'], "ctx": ctx['ctx']})
                sys.stdout.write(f"\r{params['end'] / 1000 / 1000 / end:.2f}MB/s "
                                 f"=> {params['partNumber'] / chunks:.1%}")

        start = time.perf_counter()
        await self._upload({}, file, chunk_size, upload_chunk, tasks=tasks)
        cost = time.perf_counter() - start

        print(f'[info] {filename} uploaded >> {total_size / 1000 / 1000 / cost:.2f}MB/s')
        signal_bus.log_signal.emit(f'[info] {filename} uploaded >> {total_size / 1000 / 1000 / cost:.2f}MB/s')
        parts.sort(key=lambda x: x['index'])
        self.__session.post(f"{endpoint}/mkfile/{total_size}/key/{base64.urlsafe_b64encode(key.encode()).decode()}",
                            data=','.join(map(lambda x: x['ctx'], parts)), headers=headers, timeout=10)
        r = self.__session.post(f"https:{fetch_url}", headers=fetch_headers, timeout=5).json()
        if r["OK"] != 1:
            raise Exception(r)
        return {"title": splitext(filename)[0], "filename": bili_filename, "desc": ""}

    async def upos(self, file, name, total_size, ret, tasks=3):
        filename = name
        chunk_size = ret['chunk_size']
        auth = ret["auth"]
        endpoint = ret["endpoint"]
        biz_id = ret["biz_id"]
        upos_uri = ret["upos_uri"]
        url = f"https:{endpoint}/{upos_uri.replace('upos://', '')}"  # 视频上传路径
        headers = {
            "X-Upos-Auth": auth
        }
        # 向上传地址申请上传，得到上传id等信息
        upload_id = self.__session.post(f'{url}?uploads&output=json', timeout=15,
                                        headers=headers).json()["upload_id"]
        # 开始上传
        parts = []  # 分块信息
        chunks = math.ceil(total_size / chunk_size)  # 获取分块数量

        async def upload_chunk(session, chunks_data, params):
            async with session.put(url, params=params, raise_for_status=True,
                                   data=chunks_data, headers=headers):
                end = time.perf_counter() - start
                parts.append({"partNumber": params['chunk'] + 1, "eTag": "etag"})
                sys.stdout.write(f"\r{params['end'] / 1000 / 1000 / end:.2f}MB/s "
                                 f"=> {params['partNumber'] / chunks:.1%}")
                signal_bus.log_signal.emit(f"\r{params['end'] / 1000 / 1000 / end:.2f}MB/s "
                                           f"=> {params['partNumber'] / chunks:.1%}")

        start = time.perf_counter()
        await self._upload({
            'uploadId': upload_id,
            'chunks': chunks,
            'total': total_size
        }, file, chunk_size, upload_chunk, tasks=tasks)
        cost = time.perf_counter() - start
        p = {
            'name': filename,
            'uploadId': upload_id,
            'biz_id': biz_id,
            'output': 'json',
            'profile': 'ugcupos/bup'
        }
        attempt = 0
        while attempt <= 5:  # 一旦放弃就会丢失前面所有的进度，多试几次吧
            try:
                r = self.__session.post(url, params=p, json={"parts": parts}, headers=headers, timeout=15).json()
                if r.get('OK') == 1:
                    print(f'[info] {filename} uploaded >> {total_size / 1000 / 1000 / cost:.2f}MB/s. {r}')
                    signal_bus.log_signal.emit(
                        f'[info] {filename} uploaded >> {total_size / 1000 / 1000 / cost:.2f}MB/s. {r}')
                    return {"title": splitext(filename)[0], "filename": splitext(basename(upos_uri))[0], "desc": ""}
                raise IOError(r)
            except IOError:
                attempt += 1
                print(f"请求合并分片时出现问题，尝试重连，次数：" + str(attempt))
                signal_bus.log_signal.emit(f"请求合并分片时出现问题，尝试重连，次数:{attempt}")
                time.sleep(15)

    @staticmethod
    async def _upload(params, file, chunk_size, afunc, tasks=3):
        params['chunk'] = -1

        async def upload_chunk():
            while True:
                chunks_data = file.read(chunk_size)
                if not chunks_data:
                    return
                params['chunk'] += 1
                params['size'] = len(chunks_data)
                params['partNumber'] = params['chunk'] + 1
                params['start'] = params['chunk'] * chunk_size
                params['end'] = params['start'] + params['size']
                clone = params.copy()
                for i in range(10):
                    try:
                        await afunc(session, chunks_data, clone)
                        break
                    except (asyncio.TimeoutError, ClientError) as e:
                        print(f"[error] retry chunk{clone['chunk']} >> {i + 1}. {e}")
                        signal_bus.log_signal.emit(f"[error] retry chunk{clone['chunk']} >> {i + 1}. {e}")

        async with ClientSession() as session:
            await asyncio.gather(*[upload_chunk() for _ in range(tasks)])

    def submit(self, submit_api=None):
        if not self.video.title:
            self.video.title = self.video.videos[0]["title"]
        self.__session.get('https://member.bilibili.com/x/geetest/pre/add', timeout=5)

        if submit_api is None:
            total_info = self.__session.get('http://api.bilibili.com/x/space/myinfo', timeout=15).json()
            if total_info.get('data') is None:
                print(f'[error] {total_info}')
            total_info = total_info.get('data')
            if total_info['level'] > 3 and total_info['follower'] > 1000:
                user_weight = 2
            else:
                user_weight = 1
            print(f'[info] 用户权重: {user_weight}')
            submit_api = 'web' if user_weight == 2 else 'client'
        ret = None
        if submit_api == 'web':
            ret = self.submit_web()
            if ret["code"] == 21138:
                print(f'[info] 改用客户端接口提交{ret}')
                submit_api = 'client'
        if submit_api == 'client':
            ret = self.submit_client()
        if not ret:
            raise Exception(f'不存在的选项：{submit_api}')
        if ret["code"] == 0:
            return ret
        else:
            raise Exception(ret)

    def submit_web(self):
        print('[info] 使用网页端api提交')
        return self.__session.post(f'https://member.bilibili.com/x/vu/web/add?csrf={self.__bili_jct}', timeout=5,
                                   json=asdict(self.video)).json()

    def submit_client(self):
        print('[info] 使用客户端api端提交')
        signal_bus.log_signal.emit('[info] 使用客户端api端提交')
        if not self.access_token:
            if self.account is None:
                raise RuntimeError("Access token is required, but account and access_token does not exist!")
            self.login_by_password(**self.account)
            self.store()
        while True:
            ret = self.__session.post(f'http://member.bilibili.com/x/vu/client/add?access_key={self.access_token}',
                                      timeout=5, json=asdict(self.video)).json()
            if ret['code'] == -101:
                print(f'[info] 刷新token{ret}')
                signal_bus.log_signal.emit(f'[info] 刷新token{ret}')
                self.login_by_password(**self.account)
                self.store()
                continue
            return ret

    def cover_up(self, img: str):
        """
        :param img: img path or stream
        :return: img URL
        """
        from PIL import Image
        from io import BytesIO

        with Image.open(img) as im:
            # 宽和高,需要16：10
            xsize, ysize = im.size
            if xsize / ysize > 1.6:
                delta = xsize - ysize * 1.6
                region = im.crop((delta / 2, 0, xsize - delta / 2, ysize))
            else:
                delta = ysize - xsize * 10 / 16
                region = im.crop((0, delta / 2, xsize, ysize - delta / 2))
            buffered = BytesIO()
            region.save(buffered, format=im.format)
        r = self.__session.post(
            url='https://member.bilibili.com/x/vu/web/cover/up',
            data={
                'cover': b'data:image/jpeg;base64,' + (base64.b64encode(buffered.getvalue())),
                'csrf': self.__bili_jct
            }, timeout=30
        )
        buffered.close()
        res = r.json()
        if res.get('data') is None:
            raise Exception(res)
        return res['data']['url']

    def get_tags(self, upvideo, typeid="", desc="", cover="", groupid=1, vfea=""):
        """
        上传视频后获得推荐标签
        :param vfea:
        :param groupid:
        :param typeid:
        :param desc:
        :param cover:
        :param upvideo:
        :return: 返回官方推荐的tag
        """
        url = f'https://member.bilibili.com/x/web/archive/tags?' \
              f'typeid={typeid}&title={quote(upvideo["title"])}&filename=filename&desc={desc}&cover={cover}' \
              f'&groupid={groupid}&vfea={vfea}'
        return self.__session.get(url=url, timeout=5).json()

    def __enter__(self):
        return self

    def __exit__(self, e_t, e_v, t_b):
        self.close()

    def close(self):
        """Closes all adapters and as such the session"""
        self.__session.close()


@dataclass
class Data:
    """
    cover: 封面图片，可由recovers方法得到视频的帧截图
    """
    copyright: int = 2
    source: str = ''
    tid: int = 21
    cover: str = ''
    title: str = ''
    desc_format_id: int = 0
    desc: str = ''
    dynamic: str = ''
    subtitle: dict = field(init=False)
    tag: Union[list, str] = ''
    videos: list = field(default_factory=list)
    dtime: Any = None
    open_subtitle: InitVar[bool] = False

    def __post_init__(self, open_subtitle):
        self.subtitle = {"open": int(open_subtitle), "lan": ""}
        if self.dtime and self.dtime - int(time.time()) <= 14400:
            self.dtime = None
        if isinstance(self.tag, list):
            self.tag = ','.join(self.tag)

    def delay_time(self, dtime: int):
        """设置延时发布时间，距离提交大于2小时，格式为10位时间戳"""
        if dtime - int(time.time()) > 7200:
            self.dtime = dtime

    def set_tag(self, tag: list):
        """设置标签，tag为数组"""
        self.tag = ','.join(tag)

    def append(self, video):
        self.videos.append(video)
