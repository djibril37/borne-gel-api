from app.core.security import get_password_hash
from app.database import SessionLocal
from app.models import Utilisateur, RoleEnum

print("🔧 Création/réparation de l'utilisateur admin...")

db = SessionLocal()

try:
    # Vérifiez d'abord si l'utilisateur existe
    existing = db.query(Utilisateur).filter(Utilisateur.email == "admin@bornegel.fr").first()
    
    if existing:
        print(f"⚠️  Utilisateur existe déjà: {existing.email}")
        print(f"Hash actuel: {existing.mot_de_passe_hash}")
        print(f"Longueur du hash: {len(existing.mot_de_passe_hash)}")
        
        # Générez un nouveau hash correct
        print("\n🔐 Génération d'un nouveau hash pour 'admin123'...")
        new_hash = get_password_hash("admin123")
        print(f"Nouveau hash: {new_hash}")
        print(f"Longueur nouveau hash: {len(new_hash)}")
        
        # Mettez à jour le hash
        existing.mot_de_passe_hash = new_hash
        db.commit()
        print("✅ Mot de passe mis à jour avec succès!")
        
    else:
        print("❌ Utilisateur non trouvé, création...")
        new_hash = get_password_hash("admin123")
        new_user = Utilisateur(
            email="admin@bornegel.fr",
            mot_de_passe_hash=new_hash,
            nom="Admin",
            prenom="System",
            role=RoleEnum.fournisseur
        )
        db.add(new_user)
        db.commit()
        print(f"✅ Utilisateur créé avec succès!")
        print(f"Hash généré: {new_hash}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    
finally:
    db.close()
    print("\n✨ Script terminé!")

print("\n🎯 Maintenant testez avec:")
print("curl -X POST http://localhost:8000/api/auth/login \\")
print('  -d "username=admin@bornegel.fr" \\')
print('  -d "password=admin123"')
