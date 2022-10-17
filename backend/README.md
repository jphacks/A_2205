# 実行方法

```
uvicorn main:app --reload
```

を実行して API サーバを立てる．

[localhost:8000/docs](localhost:8000/docs) にアクセスすると API のドキュメントが見れる．そこから実行もできる．


例えば，`POST /user` で自分の Twitter username を指定して叩くと初期化スクリプトが走る．そこから `POST /update` を叩くと直近の liked tweets が取得されてサーバに保存される．更にそこから `GET /tweets` を叩くと，保存された tweets が取得できる．

# API エンドポイント

- `POST /user/{username}`
    - ユーザを作成する．`username` には Twitter の username を入れる．すでに存在している場合は何も起きない．
- `DELETE /user/{username}`
    - ユーザを削除する．`username` には Twitter の username を入れる．存在しない場合は何も起きない．
- `POST /topics/{username}`
    - トピックのリストを更新する．リクエストの payload は `{"topics": [(list of topics)]}` とする．
- `GET /topics/{username}`
    - トピックのリストを取得する．レスポンスは `{"data": [(list of topics)]}` となる．
- `POST /train/{username}`
    - 学習を実行する．未実装
- `POST /update/{username}`
    - クロールを実行する．
- `GET /tweets/{username}`
    - 保存されている tweets を取得する．レスポンスは `{"data": [{レコード 1 の tweet_id, text, author_name, topic, annotated}, {レコード 2の ...}, ...]}` となる．
    - `annotated` は，ユーザが手動でアノテーションしたかどうかのフラグ
    - クエリパラメータにトピックのリストを指定されたら，指定したトピックのツイートのみ返す
- `GET /podcast`
    - podcast を作成する．未実装
