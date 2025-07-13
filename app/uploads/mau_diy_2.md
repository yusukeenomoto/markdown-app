# 自律的情報技術学習演習
2025/07/13
DS201132 榎本裕介
## AWS Amazon EC2+Docker+Flask+nginxをつかったWebサーバの構築と公開
### Markdownファイル（.md）をHTMLへ変換アプリ

[GitHub](https://github.com/yusukeenomoto/markdown-app.git)

AWSへログイン
 - 省略

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
 - ストレージを設定
     - 16 GiB へ変更

EC2インスタンスへの接続
[参考サイト](https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html)
 - SSHで接続
     - `ssh -i /path/key-pair-name.pem instance-user-name@instance-public-dns-name`
     - もう少しわかりやすいサンプル
     - `ssh -i /path/key-pair-name.pem ec2-user@パブリックIPv4アドレス`
         - 接続に成功すると鳥のイラストが出る
         - `uname -a` でOSを確認する
     - ルート権限にパスワードは不要
 - dnf update
     - `sudo dnf update -y`
     - `sudo dnf upgrade -y`

Docker関連の下準備
 - Dockerのインストール、起動
 - そのままでは、docker compose がインストールされないので注意
     - `sudo dnf install -y docker`
     - `sudo systemctl start docker`
     - `sudo systemctl enable docker`
         - "Hello from Docker!"などの返り値があればOK
     - Docker Composeをダウンロード（V2）ローカルのDocker Desktopに合わせた
         - `sudo mkdir -p /usr/local/lib/docker/cli-plugins`
         - `sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose`
         - `sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose`
     - 以下のコマンドで動作を確認する
     - `sudo docker run hello-world`

 - Dockerfileの作成
     - GitHub CLIのインストール
     - [参考サイト](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)
     - 公式リポジトリに入っていなかったので、追加
         - dnfの系統を調べる(4系だった)
         - `dnf --version`
     - `sudo dnf install 'dnf-command(config-manager)'`
     - `sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo`
         - "Adding repo from: https://cli.github.com/packages/rpm/gh-cli.repo" が返ってくればOK
     - インストール失敗`sudo dnf install gh --repo gh-cli`
     - `sudo dnf install gh`
         - こちらがインストールできた
         - `which gh`
             - インストールできたか確認
     - GitHub のリポジトリからcloneする
     - 今回はPublicリポジトリからのcloneなので、認証不要だが、
     - `gh repo clone yusukeenomoto/markdown-app`
         - "gh auth login"が必要といわれる
             - トークンを作成
             - GitHub(webサイト) → 右上のプロフィールアイコン → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token
             - 環境変数へ入れる
             - `echo 'export GH_TOKEN=ghp_your_token_here' >> ~/.bashrc`
             - `source ~/.bashrc`
             - 以下で確認する
             - `gh auth status`
         - GitHub Actionsでの更新も検討 

Dockerコンテナの起動
- コンテナの仕様
    - Flaskコンテナ
        - python:3.12-slim 
        - Python-Markdownライブラリでhtmlへ変換
    - nginxコンテナ
        - nginx:latest
        - リバースプロキシとして動作し、外部からのリクエストをFlaskへ転送
        - 静的サイトのホスティング
- Dockerの起動
    - `cd markdown-app`
    - `docker compose up -d`
- サイトの起動確認
    - 別のターミナルから確認する
    - `curl パブリックIPv4アドレス`
        - 静的サイトが表示される
    - `curl パブリックIPv4アドレス/app`
        - Flaskのアップロードサイトが表示される 

---

Flask
 - app.py
     - Python-Markdownライブラリを使用時、"-"などのリストへの変換がうまくいかない（"-"の前行に空行が必要）
     - 他のライブラリ（markdown2）の使用を検討したが、コードブロックへの装飾がうまくいかない可能性があったため不採用
     - reモジュールで空行を追加する関数で対応