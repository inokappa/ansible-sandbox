# ansible-sandbox

## modules

### library/datadog_tags.py

Datadog のタグを管理するモジュールで、以下の何れかのディレクトリに放り込むことで利用が可能です。

- カレントディレクトリの `library` ディレクトリ
- 環境変数 `ANSIBLE_LIBRARY` で指定されたパス
- ansible.cfg で指定されたパス
- `--module-path` で指定されたパス

Playbook は以下のように記述します。

```yaml
- name: Test datadog_tags(present)
  datadog_tags:
    state: present
    host: MyHost
    tags: 'aa,bb,cc,dd'
    api_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    app_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- name: Test datadog_tags(absent)
  datadog_tags:
    state: absent
    host: MyHost
    api_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    app_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

`host` には Datadog で登録されているホスト名を記述する必要があります。

## plugins

### plugins/cloudwatch_logs.py

Ansible 実行時の各イベントを Cloudwatch Logs に転送する callback plugin です。

ansible.cfg に定義されている `callback_plugins` のパスに放り込んで `callback_whitelist` にプラグイン名を記載することで利用が可能です。

```
[default]
callback_plugins = ~/path/to/plugins
callback_whitelist = cloudwatch_logs
```

Role からも呼び出すことが出来るようです。
