# DPT

DPT is a QA-bot designed to help answer questions about DagsHub. It is a fork of the brilliant [buster](https://github.com/jerpint/buster) project. Using DagsHub's [documentation](https://dagshub.com/docs) as reference and [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for sentence similarity, we identify documents that contain relevant information to a given query. This is then passed to OpenAI's GPT-3.5 Turbo, that uses the information and the query given a prompt to return an answer to the user query, that's hopefully helpful.

Currently, we're working on the following changeset:
- [x] Using VectorDBs over pythonic semantic clustering
- [ ] Better hallucination detection
- [ ] Fine-grained document splitting with lookback window

## Using DPT

### Via Discord

DPT is available as a bot on Discord. Join our [server](https://discord.gg/Fn8fMsJFa3) and check out #support!

### Locally

**Note:** DVC has a bug where it doesn't correctly interpret submodules. Please remove `.gitmodules` before running DVC commands, then run `git checkout HEAD -- /path/to/project/root/.gitmodules` to reset it back to the original state.

1. Pull the repository *with* submodules: clone with the `--recurse-submodules` flag, or `git submodule update --init` if the repo is already cloned. The pull from the DVC remote using `dvc pull -r origin`.
2. To use DPT locally, you will need an [OpenAI Access Key](https://platform.openai.com/account/api-keys).
3. Set that in a `.env` file with the format `OPENAI_API_KEY=<key>` in the root of the project.
4. Run `python -m src.chat.converse` from the project root. This sets up a very minimal conversational client that you can use to play with DPT.
5. (Optional) If you would like to use it as a discord bot, create a discord application through their [developer portal](https://discord.com/developers/applications).
6. Add the bot's token to the `.env` file with the format `DISCORD_TOKEN=<token>`.
7. Run `python -m src.discord.bot`.

## Contributing

If you would like to help out, please check our [active issues](https://dagshub.com/DagsHub/DPT/issues?type=all&state=open&labels=208&milestone=0&assignee=0) for tasks labelled 'help wanted'. Please fork our project, and create a PR; we will review it as soon as possible.
