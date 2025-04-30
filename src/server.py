from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.llm import register_api_llm
from api.paco import register_paco_api
import uvicorn
# https://blog.futuresmart.ai/integrating-google-authentication-with-fastapi-a-step-by-step-guide
# http://youtube.com/watch?v=B5AMPx9Z1OQ&list=PLqAmigZvYxIL9dnYeZEhMoHcoP4zop8-p&index=26
# https://www.youtube.com/watch?v=bcYmfHOrOPM
# TO EMBED DASH IN FASAPI
# https://medium.com/@gerardsho/embedding-dash-dashboards-in-fastapi-framework-in-less-than-3-mins-b1bec12eb3
# swaggerui al link  http://127.0.0.1:8000/docs
# server al link http://127.0.0.1:8000/


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