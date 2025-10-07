from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.llm import register_api_llm
from src.api.paco import register_paco_api
import uvicorn

def run(port: int = 8000):
	app = FastAPI()
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"]
	)

	@app.get("/")
	async def get():
		"""
		Root endpoint that returns a welcome message
		Returns:
			str: Welcome message
		"""
		return f"welcome to PACO server"

	register_paco_api(app)
	register_api_llm(app)

	uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
	run()