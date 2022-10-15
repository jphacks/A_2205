# 実行方法

```
uvicorn main:app --reload
```

を実行して API サーバを立てる．

[localhost:8000/docs](localhost:8000/docs) にアクセスすると API のドキュメントが見れる．そこから実行もできる．


例えば，`/create_user` で自分の Twitter username を指定して叩くと初期化スクリプトが走る．そこから `/update` を叩くと直近の liked tweets が取得されてサーバに保存される．更にそこから `/tweets` を叩くと，保存された tweets が取得できる．

# API エンドポイント

- `GET /create_user/{username}`
    - ユーザを作成する．`username` には Twitter の username を入れる．すでに存在している場合は何も起きない．
- `POST /train/{username}`
    - 学習を実行する．未実装
- `POST /update/{username}`
    - クロールを実行する
- `GET /tweets/{username}`
    - 保存されている tweets を取得する
- `GET /podcast`
    - podcast を作成する．未実装
