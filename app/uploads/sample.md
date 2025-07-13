# 自律的情報技術学習演習
2025/07/12
DS201132 榎本裕介
## AWS Amazon EC2+Docker+Flask+nginxをつかったWebサーバの構築と公開

AWSへログイン
省略

EC2インスタンスの作成

 - リージョン: ap-northeast-1
 - OS: Amazon Linux
 - インスタンスタイプ: t3.micro
 - キーペア: ED25519
     - キーペア作成後、パーミッションを変更、~/.ssh へ格納する
     - `chmod 400 key-pair-name.pem`
     - `mv 400 key-pair-name.pem ./ssh`
 - SSH: SSH トラフィックを許可 へチェックを入れる
     - 任意の場所（0.0.0.0/0） とした
 - インターネットからの HTTP トラフィックを許可 へチェックを入れる
     - nginxでwebサーバーを公開するため