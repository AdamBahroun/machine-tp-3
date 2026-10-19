# code/essai.py : test de connexion à l'API
import os, sys
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
modele = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-oss-20b"
reponse = client.chat.completions.create(
    model=modele,
    messages=[{"role": "user", "content": "Réponds : OK"}])
print(reponse.choices[0].message.content)
