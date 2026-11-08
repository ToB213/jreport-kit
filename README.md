# 日本語レポート作成ツール

研究の進捗報告などの短い日本語レポートを、upLaTeX と latexmk で作成するツールです。

## 目次

- [概要](#概要)
- [導入](#導入)
- [使い方](#使い方)
- [不具合報告と改善提案](#不具合報告と改善提案)
- [ライセンス](#ライセンス)

## 概要

日付別の雛形作成、PDF ビルド、変更監視、ブラウザプレビューに対応しています。
標準の書式は A4・余白 25 mm で、題名・日付・発表者・ページ番号を表示します。

## 導入

### 必要な環境

- Python 3.9 以降
- 日本語組版に対応した TeX 環境（TeX Live など）
- `latexmk`、`uplatex`、`dvipdfmx`（引用を使う場合は `upbibtex` も必要）

ブラウザプレビューのビルド停止処理には POSIX のプロセス制御を使うため、macOS / Linux を対象としています。

### セットアップ

Python と上記の TeX コマンドが PATH にあれば、そのまま実行できます。

```sh
python3 scripts/report.py --help
```

Nix を使う場合は、代わりに次のコマンドで必要な環境を読み込めます。
`nix-command` と `flakes` を有効にしてください。

```sh
nix develop
```

## 使い方

### レポートの作成とビルド

```sh
python3 scripts/report.py new 2026-11-06
```

生成された `reports/2026/2026-11-06/main.tex` に題名・発表者・本文を記入します。

```sh
python3 scripts/report.py build 2026-11-06
```

PDF は `build/2026-11-06/main.pdf` に生成されます。日付は `YYYY-MM-DD` で指定します。
同じ日付のレポートがある場合、`new` は上書きせず終了します。

### プレビュー

```sh
python3 scripts/report.py preview 2026-11-06
```

`http://127.0.0.1:8000/` をブラウザで開き、本文・画像・文献・書式の変更時に再ビルドします。

プレビューはローカル接続のみ受け付けます。更新時のページ位置やズームの維持には対応していません。
別の PDF ビューアを使う場合は、次のコマンドで変更を監視し、生成された PDF を手動で開きます。

```sh
python3 scripts/report.py watch 2026-11-06
```

### 画像・文献・書式

画像は各レポートの `images/` に置き、本文から読み込みます。

```tex
\includegraphics[width=.8\linewidth]{figure.png}
```

文献とセミナー用書式には、コピーして使う `.example` ファイルを用意しています。

- [文献の設定と引用](bib/README.md)
- [セミナー用ヘッダー・フッターの設定](sty/README.md)

新規レポートの本文を変える場合は、[template/report.tex](template/report.tex) を編集してください。

## 不具合報告と改善提案

不具合や改善案は GitHub Issues へ、変更は Pull Request で送ってください。
不具合報告には OS、実行コマンド、エラーメッセージを添えてください。レポート本文などの個人情報は除いてください。

## ライセンス

[MIT License](LICENSE)
