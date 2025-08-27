import requests
import os
import re
from shutil import copyfile
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import chardet
import tempfile
import shutil
import sys

"""检测文件编码（支持二进制数据检测"""
def detect_encoding(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
            confidence = result['confidence']
            
            if confidence < 0.6:
                print(f"⚠️ 低置信度({confidence:.1%})检测编码: {encoding}，使用替换策略")
                return encoding, 'replace'
            return encoding, None
    except Exception as e:
        print(f"❌ 检测编码失败: {file_path} - {str(e)}")
        return 'utf-8', 'replace'  # 默认使用utf-8

"""递归遍历目录，实时上传每个文件（增加进度计数和错误处理）"""
def traverse_and_upload(directory):
    # 先统计PHP文件总数
    total_php_files = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.php'):
                total_php_files += 1
                
    print(f"📊 总共发现 {total_php_files} 个PHP文件")
    
    # 初始化计数器
    current_count = 0
    success_count = 0
    skip_count = 0
    error_count = 0
    
    # 遍历处理文件
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            if filename.endswith('.php'):
                current_count += 1
                print(f"\n📁 处理文件 ({current_count}/{total_php_files}): {file_path}")
                
                try:
                    # 先以二进制读取检查特定标记
                    with open(file_path, 'rb') as bin_file:
                        file_body = bin_file.read(2000)
                    
                    if b'<?php //004fb' in file_body:
                        # 检测编码并读取完整内容
                        encoding, error_handling = detect_encoding(file_path)
                        open_args = {'encoding': encoding, 'errors': error_handling} if error_handling else {'encoding': encoding}
                        
                        with open(file_path, 'r', **open_args) as f:
                            content = f.read()
                        
                        # 上传文件
                        print(f"⬆️ 上传文件: {filename}")
                        download = UploadFile(filename, content)
                        
                        if download:
                            # 下载并覆盖
                            if download_and_overwrite(download, file_path):
                                success_count += 1
                                print(f"✅ 文件处理成功: {filename}")
                            else:
                                error_count += 1
                                print(f"❌ 下载覆盖失败: {filename}")
                        else:
                            error_count += 1
                            print(f"❌ 上传失败: {filename}")
                    else:
                        skip_count += 1
                        print("⏩ 跳过未加密文件")
                except Exception as e:
                    error_count += 1
                    print(f"🔥 处理文件时发生异常: {str(e)}")
                    # 记录错误日志
                    with open('error_log.txt', 'a') as log_file:
                        log_file.write(f"Error in {file_path}: {str(e)}\n")
            else:
                print(f"⏩ 跳过非PHP文件: {filename}")
    
    # 输出最终统计报告
    print("\n" + "="*50)
    print(f"📊 任务完成报告:")
    print(f"✅ 成功处理: {success_count} 个文件")
    print(f"⏩ 跳过文件: {skip_count} 个（未加密或非PHP）")
    print(f"❌ 处理失败: {error_count} 个文件")
    print(f"📋 错误日志已保存到: error_log.txt")
    print("="*50)

# 上传文件（增加错误处理）
def UploadFile(filename, php):
    try:
        proxy = {'http': '127.0.0.1:8080', 'https': '127.0.0.1:8080'}
        decode_url = "https://easytoyou.eu:443/decoder/ic11php74"
        decode_cookies = {"PHPSESSID": "no9p9pcmbkmfem4kb80qiglvi5", "_ga": "GA1.1.1870566490.1755502099", "_ga_GK60DC8FLY": "GS2.1.s1756255877$o10$g1$t1756257940$j60$l0$h0"}
        decode_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"macOS\"", "Origin": "https://easytoyou.eu", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryMveNXoSCfqKpuxwy", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://easytoyou.eu/decoder/ic11php74", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9", "Priority": "u=0, i"}
        
        decode_data = "------WebKitFormBoundaryMveNXoSCfqKpuxwy\r\nContent-Disposition: form-data; name=\"022708[]\"; filename=\"" + filename + "\"\r\nContent-Type: text/php\r\n\r\n" + php + "\r\n------WebKitFormBoundaryMveNXoSCfqKpuxwy\r\nContent-Disposition: form-data; name=\"submit\"\r\n\r\nDecode\r\n------WebKitFormBoundaryMveNXoSCfqKpuxwy--\r\n"
        res = requests.post(decode_url, headers=decode_headers, cookies=decode_cookies, 
                           data=decode_data, timeout=25, verify=False, proxies=proxy)
        
        if res.status_code == 200 and re.findall(r"Download link: <a href='", res.text):
            print(f"✅ 上传成功: {filename}")
            download = re.findall(r"Download link: <a href='(.+?)'>", res.text)[0]
            return download
            
        elif re.findall(r"can't be decoded.", res.text):
            skip_path = os.path.join('写入你的报错内容保存地址', filename)
            copyfile(filename, skip_path)
            print(f'⚠️ 未加密或类型不正确: {filename}')
            return None
        else:
            print(f'❌ 上传错误: HTTP {res.status_code}')
            with open('upload_errors.txt', 'a') as f:
                f.write(f"{filename} - HTTP {res.status_code}\n")
            return None
            
    except Exception as e:
        print(f'🔥 上传过程中发生异常: {str(e)}')
        with open('upload_errors.txt', 'a') as f:
            f.write(f"{filename} - Exception: {str(e)}\n")
        return None

"""下载文件并原子覆盖原文件（增加错误处理）"""
def download_and_overwrite(download_url, original_path):
    try:
        burp0_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"macOS\"", "Origin": "https://easytoyou.eu", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryMveNXoSCfqKpuxwy", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://easytoyou.eu/decoder/ic11php74", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "zh-CN,zh;q=0.9", "Priority": "u=0, i"}

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_path = tmp_file.name
            
            # 流式下载
            with requests.get(download_url, headers=burp0_headers, timeout=25, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
        
        # 原子覆盖原文件
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        shutil.move(temp_path, original_path)
        print(f"✅ 文件替换成功: {original_path}")
        return True
        
    except requests.HTTPError as e:
        print(f'❌ 下载HTTP错误: {str(e)}')
        return False
    except Exception as e:
        print(f'🔥 下载过程中发生异常: {str(e)}')
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return False

if __name__ == '__main__':
    try:
        target_dir = '填入你的需要解密的项目目录'
        print(f"🚀 开始处理目录: {target_dir}")
        traverse_and_upload(target_dir)
        print("🎉 所有文件处理完成！")
    except KeyboardInterrupt:
        print("\n🛑 用户中断操作！")
        sys.exit(1)
    except Exception as e:
        print(f"🔥 主程序发生未处理异常: {str(e)}")
        sys.exit(1)
