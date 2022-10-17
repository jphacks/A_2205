# 実行方法

```
uvicorn main:app --reload
```

を実行して API サーバを立てる．

[localhost:8080/docs](localhost:8080/docs) にアクセスすると API のドキュメントが見れる．そこから実行もできる．


例えば，`POST /user` で自分の Twitter username を指定して叩くと初期化スクリプトが走る．そこから `POST /update` を叩くと直近の liked tweets が取得されてサーバに保存される．更にそこから `GET /tweets` を叩くと，保存された tweets が取得できる．

# API エンドポイント

- `POST /user/{username}`
    - ユーザを作成する．`username` には Twitter の username を入れる．
- `DELETE /user/{username}`
    - ユーザを削除する．`username` には Twitter の username を入れる．
- `POST /topics/{username}`
    - トピックのリストを更新する．リクエストの payload は `{"topics": [(list of topics)]}` とする．
- `GET /topics/{username}`
    - トピックのリストを取得する．レスポンスは `{"data": [(list of topics)]}` となる．
- `POST /train/{username}`
    - 学習を実行する．ユーザがラベル付けした (id, label) のペアを payload にして送ると，それを元に学習を行ってモデルを更新し，それを既存のデータに対して適用する (未実装)．
- `POST /update/{username}`
    - クロールを実行する．直近 100 件の fav が取得される (Twitter API の仕様上それ以上はできない？)．２回目以降は差分のみ (100 件を超える場合は直近 100 件のみ) 追加する．
- `GET /tweets/{username}`
    - 保存されている tweets を取得する．レスポンスは `{"data": [{レコード 1 の tweet_id, text, author_name, topic, annotated}, {レコード 2の ...}, ...]}` となる．
    - `annotated` は，ユーザが手動でアノテーションしたかどうかのフラグ
    - クエリパラメータにトピックのリストを指定されたら，指定したトピックのツイートのみ返す
- `GET /podcast`
    - podcast を作成する (未実装)．
