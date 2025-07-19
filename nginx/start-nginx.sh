#!/bin/sh
# nginx/start-nginx.sh

echo "=== Nginx Startup Script ==="
echo "DOMAIN: $DOMAIN"
echo "DOMAIN_WWW: $DOMAIN_WWW"

# 環境変数を設定ファイルに展開
echo "Generating nginx configuration..."
envsubst '$DOMAIN,$DOMAIN_WWW' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# 生成された設定ファイルの確認
echo "Generated nginx config preview:"
grep -E "server_name|ssl_certificate" /etc/nginx/conf.d/default.conf | head -5

# Nginxの設定テスト
echo "Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# バックグラウンドで6時間ごとにNginx設定を再読み込み
echo "Starting background reload process..."
while :; do
    sleep 6h &
    wait $!
    echo "$(date): Reloading nginx configuration..."
    nginx -s reload
done &

# Nginxをフォアグラウンドで起動
echo "Starting nginx daemon..."
nginx -g 'daemon off;'