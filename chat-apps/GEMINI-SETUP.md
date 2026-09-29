# Gemini: CLI extension and app Gem

## Gemini CLI

Install the extension from this repository:

```sh
gemini extensions install https://github.com/dogancoban/deep-research-companion --ref main
```

Restart Gemini CLI, then ask: “Use Deep Research Companion to check this answer and its sources.” The extension exposes the existing `deep-research-companion` skill.

Check installation with `gemini extensions list`. Update with `gemini extensions update deep-research-companion`. Source checking needs web access; document generation needs the dependencies listed in README.md.

## Gemini app (Gem)

1. Open https://gemini.google.com/gems/view .
2. If a Deep Research Companion / Kanıt Hattı Gem already exists, edit it instead of making a duplicate. Otherwise select New Gem.
3. Name: **Kanıt Hattı — Deep Research Companion**.
4. Instructions: paste the complete contents of [instructions.md](instructions.md).
5. Save. Start a chat and paste an answer with its source URLs.

The Gem supports prompt writing and answer checking using the tools available in Gemini. It does not run the local Python/Node report pipeline. If browsing cannot retrieve a source, the result must remain unverified.

## Validation

Manifest JSON and bundled skill paths are checked. CLI installation is checked separately; this does not establish end-to-end research or report-generation accuracy.

Official references: https://geminicli.com/docs/extensions/reference/ and https://support.google.com/gemini/answer/15146780
