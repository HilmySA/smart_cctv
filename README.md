Get started by customizing your environment (defined in the .idx/dev.nix file) with the tools and IDE extensions you'll need for your project!

Learn more at https://developers.google.com/idx/guides/customize-idx-env

#MICROSERVICE ML
- source .venv/bin/activate
- uvicorn app.main:app --host 0.0.0.0 --port 8000

#FRONTEND
- npm run dev