# 🚀 Comment tester l'API Borne Gel

## 📍 URL de l'API
https://vigilant-eureka-694g4v6w6p9xcg7x-8000.app.github.dev

## 🔐 Compte de test
Email: admin@bornegel.fr
Mot de passe: admin123

## 📖 Documentation interactive
- **Swagger UI** (tester directement) : https://vigilant-eureka-694g4v6w6p9xcg7x-8000.app.github.dev/docs
- **Redoc** (lire la doc) : https://vigilant-eureka-694g4v6w6p9xcg7x-8000.app.github.dev/redoc

## 🔧 Test avec Postman

### Étape 1 : Login
1. **Méthode** : POST
2. **URL** : `https://vigilant-eureka-694g4v6w6p9xcg7x-8000.app.github.dev/api/auth/login`
3. **Body** : Sélectionnez `x-www-form-urlencoded`
4. **Paramètres** :
   - `username`: admin@bornegel.fr
   - `password`: admin123

### Étape 2 : Récupérer le token
Si le login réussit, vous recevrez :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}