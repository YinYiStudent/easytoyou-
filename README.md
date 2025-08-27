# easytoyou批量解密脚本 【10欧元10天使用Paypal支付即可】

1.修改Cookie和项目目录地址可完成自动化解密

2.将原文件直接覆盖

## 修改几个地方即可使用：

1.代码第107行，我这里使用的是burp代理，自行更改

​	`proxy = {'http': '127.0.0.1:8080', 'https': '127.0.0.1:8080'}`

1.代码第108行，改成你自己的解密版本的Url

​	 `decode_url = "https://easytoyou.eu:443/decoder/ic11php74"`

2.代码第109行，登陆后将你自己的Cookie改成你自己的

​	 `decode_cookies = {"PHPSESSID": "变成你的", "_ga": "变成你的", "_ga_GK60DC8FLY": "变成你的"}`

3.代码第112行，修改name=\"XXXXX[]"中的X，将你正常上传后所获取到的数字填入内，要不然上传报错

4.代码第122行，改成你的报错内容保存地址

   `skip_path = os.path.join('写入你的报错内容保存地址', filename)`

5.代码第171行，改成你的需要解密的项目目录

`target_dir = '填入你的需要解密的项目目录'`