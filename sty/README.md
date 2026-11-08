# セミナー用書式

`seminar.sty.example` は、題名・日付・発表者をヘッダーに、ページ番号と総ページ数をフッターに表示する書式です。

```sh
cp -n sty/seminar.sty.example sty/seminar.sty
```

レポートのプリアンブルで、`\pagestyle{plain}` の後に追加します。

```tex
\usepackage{sty/seminar}
\seminar{Title}{報告タイトル}
\seminar{Date}{2026年11月6日}
\seminar{Presenter}{発表者名}
```

本文のタイトルが不要な場合は、雛形の `center` 環境を削除してください。

[README に戻る](../README.md)
