import requests

url = "http://localhost:3000/api/licenses"
headers = {"X-API-Key": "FXA-Kj8$mN2@pQ9#vX5!wY3&zL7*"}

response = requests.get(url, headers=headers)
print("Код ответа:", response.status_code)
print("Ответ сервера:")
print(response.text)

input("\nНажми Enter...")