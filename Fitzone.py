import uuid
from abc import ABC, abstractmethod

class Outils:
    @staticmethod
    def generer_id(prefixe="ID"):
        """Génère un identifiant court et unique."""
        return f"{prefixe}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def appliquer_reduction(tarif, age_membre):
        """
        Applique -20% pour les mineurs (< 18 ans) et les seniors (>= 60 ans).
        """
        if age_membre < 18 or age_membre >= 60:
            return round(tarif * 0.8, 2)
        return round(tarif, 2)

class Seance(ABC):
    def __init__(self, nom, coach):
        self.id_seance = Outils.generer_id("SEA")
        self.nom = nom
        self.coach = coach
        self.participants = []  
        self.liste_attente = []  
    @abstractmethod
    def calculer_tarif(self):
        """Calcule le tarif de base de la séance."""
        pass

    @abstractmethod
    def capacite_max(self):
        """Retourne la capacité maximale de la séance."""
        pass

    def __str__(self):
        type_seance = self.__class__.__name__
        places_libres = self.capacite_max() - len(self)
        return (f"[{self.id_seance}] {self.nom} (Coach: {self.coach}) | "
                f"Type: {type_seance} | Places: {len(self)}/{self.capacite_max()} "
                f"(Libres: {places_libres})")

    def __eq__(self, other):
        if not isinstance(other, Seance):
            return False
        return self.id_seance == other.id_seance

    def __len__(self):
        return len(self.participants)


class CoursCollectif(Seance):
    def __init__(self, nom, coach, cout_base=150.0):
        super().__init__(nom, coach)
        self.cout_base = float(cout_base)

    def capacite_max(self):
        return 15  

    def calculer_tarif(self):
        
        nb_part = len(self) if len(self) > 0 else 1
        return round(self.cout_base / nb_part, 2)


class CoachingPersonnel(Seance):
    def __init__(self, nom, coach, tarif_horaire=60.0):
        super().__init__(nom, coach)
        self.tarif_horaire = float(tarif_horaire)

    def capacite_max(self):
        return 1 

    def calculer_tarif(self):
        return round(self.tarif_horaire, 2)

class Membre:
    def __init__(self, nom, age):
        self.id_membre = Outils.generer_id("MEM")
        self.nom = nom
        try:
            self.age = int(age)
        except ValueError:
            self.age = 18  
        self.reservations = []  

    def reserver(self, seance):
        """Ajoute une séance aux réservations du membre."""
        if seance not in self.reservations:
            self.reservations.append(seance)
            return True
        return False

    def annuler(self, seance):
        """Retire une séance des réservations du membre."""
        if seance in self.reservations:
            self.reservations.remove(seance)
            return True
        return False

    def __len__(self):
        return len(self.reservations)

    def __str__(self):
        return f"[{self.id_membre}] {self.nom} ({self.age} ans) - {len(self)} réservation(s)"

class Salle:
    nb_reservations_total = 0  

    def __init__(self, nom):
        self.nom = nom
        self.seances = {}  
        self.membres = {}  

    def inscrire_membre(self, nom, age):
        nouveau = Membre(nom, age)
        self.membres[nouveau.id_membre] = nouveau
        print(f"✔️ Membre inscrit avec succès : {nouveau}")
        return nouveau

    def ajouter_seance(self, seance):
        self.seances[seance.id_seance] = seance
        print(f"✔️ Séance planifiée : {seance}")

    def reserver_seance(self, id_membre, id_seance):
        membre = self.membres.get(id_membre)
        seance = self.seances.get(id_seance)

        if not membre:
            print("❌ Erreur : Membre introuvable.")
            return False
        if not seance:
            print("❌ Erreur : Séance introuvable.")
            return False

        if seance in membre.reservations:
            print("⚠️ Ce membre a déjà réservé cette séance.")
            return False

        if len(seance) >= seance.capacite_max():
            print(f"❌ La séance est complète ({seance.capacite_max()} places max).")
        
            reponse = input("Voulez-vous inscrire le membre sur la liste d'attente ? (o/n) : ").strip().lower()
            if reponse == 'o':
                if membre not in seance.liste_attente:
                    seance.liste_attente.append(membre)
                    print(f"📝 {membre.nom} a été ajouté à la liste d'attente de la séance.")
                else:
                    print("⚠️ Le membre est déjà dans la liste d'attente.")
            return False

        seance.participants.append(membre)
        membre.reserver(seance)
        Salle.nb_reservations_total += 1
        print(f"🎉 Réservation confirmée pour {membre.nom} au cours '{seance.nom}'.")
        return True

    def annuler_reservation(self, id_membre, id_seance):
        membre = self.membres.get(id_membre)
        seance = self.seances.get(id_seance)

        if not membre or not seance:
            print("❌ Erreur : Membre ou séance introuvable.")
            return False

        if seance not in membre.reservations:
            print("❌ Erreur : Aucune réservation active trouvée pour ce membre sur cette séance.")
            return False

        seance.participants.remove(membre)
        membre.annuler(seance)
        Salle.nb_reservations_total = max(0, Salle.nb_reservations_total - 1)
        print(f"✔️ Réservation annulée pour {membre.nom}.")

        if seance.liste_attente:
            prochain_membre = seance.liste_attente.pop(0)
            print(f"🔔 Une place se libère ! Attribution automatique à {prochain_membre.nom} (liste d'attente).")
            seance.participants.append(prochain_membre)
            prochain_membre.reserver(seance)
            Salle.nb_reservations_total += 1

        return True

    def rechercher_avancee(self, **kwargs):
        """
        Filtres possibles : coach, type_seance, disponible (True/False)
        """
        resultats = list(self.seances.values())

        if 'coach' in kwargs and kwargs['coach']:
            recherche_coach = kwargs['coach'].lower()
            resultats = [s for s in resultats if recherche_coach in s.coach.lower()]

        if 'type_seance' in kwargs and kwargs['type_seance']:
            t = kwargs['type_seance'].lower()
            resultats = [s for s in resultats if t in s.__class__.__name__.lower()]

        if 'disponible' in kwargs:
            if kwargs['disponible']:
                resultats = [s for s in resultats if len(s) < s.capacite_max()]
            else:
                resultats = [s for s in resultats if len(s) >= s.capacite_max()]

        return resultats

    def afficher_statistiques(self):
        print("\n" + "=" * 40)
        print("          STATISTIQUES DE LA SALLE      ")
        print("=" * 40)
        print(f"• Nombre total de membres : {len(self.membres)}")
        print(f"• Nombre total de séances créées : {len(self.seances)}")
        print(f"• Cumul historique des réservations : {Salle.nb_reservations_total}")

        if not self.seances:
            print("• Aucune séance enregistrée pour établir un classement.")
            return

        seances_triees = sorted(self.seances.values(), key=lambda s: len(s), reverse=True)

        print("\n🏆 CLASSEMENT DE POPULARITÉ DES SÉANCES :")
        for i, s in enumerate(seances_triees, 1):
            print(f"  {i}. {s.nom} ({len(s)} participants)")

def input_securise(prompt, type_attendu=str, min_val=None, max_val=None):
    """Demande une saisie à l'utilisateur avec un maximum de 3 essais."""
    tentatives = 3
    while tentatives > 0:
        saisie = input(prompt).strip()
        if not saisie:
            tentatives -= 1
            print(f"⚠️ Saisie vide. Il vous reste {tentatives} essai(s).")
            continue
        try:
            valeur = type_attendu(saisie)
            if min_val is not None and valeur < min_val:
                raise ValueError(f"La valeur doit être supérieure ou égale à {min_val}.")
            if max_val is not None and valeur > max_val:
                raise ValueError(f"La valeur doit être inférieure ou égale à {max_val}.")
            return valeur
        except ValueError as e:
            tentatives -= 1
            print(f"❌ Entrée invalide ({e}). Il vous reste {tentatives} essai(s).")

    print("⛔ Trop de tentatives infructueuses. Retour au menu principal.")
    return None

def initialiser_demonstration(salle):
    print("\n--- Initialisation du jeu de données de démonstration ---")

    m1 = salle.inscrire_membre("Alice Cooper", 17)  
    m2 = salle.inscrire_membre("Bob Marley", 45)
    m3 = salle.inscrire_membre("Charlie Chaplin", 72)  

    s1 = CoursCollectif("Vinyasa Yoga Zen", "Sarah", cout_base=120.0)
    s2 = CoursCollectif("Cardio Boxing", "Mike", cout_base=180.0)
    s3 = CoursCollectif("Pilates Abdos", "Sarah", cout_base=150.0)

    s4 = CoachingPersonnel("Personal Training Élite", "Mike", tarif_horaire=50.0)
    s5 = CoachingPersonnel("Nutrition & Renfo", "Jean", tarif_horaire=70.0)
    s6 = CoachingPersonnel("Prépa Physique Marathon", "David", tarif_horaire=90.0)

    for s in [s1, s2, s3, s4, s5, s6]:
        salle.ajouter_seance(s)

    s1.capacite_max = lambda: 1

    print("\n--- Simulation de réservations ---")
    salle.reserver_seance(m1.id_membre, s1.id_seance)  
    salle.reserver_seance(m1.id_membre, s4.id_seance) 
    salle.reserver_seance(m2.id_membre, s2.id_seance)  
    salle.reserver_seance(m2.id_membre, s5.id_seance)  
    salle.reserver_seance(m3.id_membre, s2.id_seance)  

    print("\n--- Tentative sur cours complet (Yoga - Max 1 place, déjà prise par Alice) ---")
    salle.reserver_seance(m2.id_membre, s1.id_seance) 

def afficher_menu():
    print("\n" + "=" * 45)
    print("           FITZONE - MENU GESTION           ")
    print("=" * 45)
    print("1. Inscrire un nouveau membre")
    print("2. Ajouter une séance au planning")
    print("3. Réserver une séance")
    print("4. Annuler une réservation")
    print("5. Calculer le tarif d'une séance (avec réduction)")
    print("6. Recherche avancée de séances (Filtres)")
    print("7. Afficher les réservations d'un membre")
    print("8. Afficher les statistiques et la popularité")
    print("9. Quitter")
    print("=" * 45)


def main():
    ma_salle = Salle("FitZone Club")
    initialiser_demonstration(ma_salle)

    while True:
        afficher_menu()
        choix = input("Votre choix (1-9) : ").strip()

        if choix == "1":
            print("\n--- INCRIPTION NOUVEAU MEMBRE ---")
            nom = input_securise("Nom du membre : ")
            if not nom: continue
            age = input_securise("Âge du membre : ", int, min_val=10, max_val=100)
            if age is None: continue

            ma_salle.inscrire_membre(nom, age)

        elif choix == "2":
            print("\n--- AJOUTER UNE SÉANCE ---")
            nom_cours = input_securise("Nom de la séance : ")
            if not nom_cours: continue
            coach = input_securise("Nom du coach : ")
            if not coach: continue

            print("Type de séance : ")
            print("  1. Cours Collectif")
            print("  2. Coaching Personnel")
            type_choix = input_securise("Votre choix (1 ou 2) : ", int, min_val=1, max_val=2)
            if type_choix is None: continue

            if type_choix == 1:
                cout = input_securise("Coût de base de la séance collective (ex: 150) : ", float, min_val=10.0)
                if cout is None: continue
                nouvelle_seance = CoursCollectif(nom_cours, coach, cout)
            else:
                tarif = input_securise("Tarif horaire du coaching (ex: 60) : ", float, min_val=10.0)
                if tarif is None: continue
                nouvelle_seance = CoachingPersonnel(nom_cours, coach, tarif)

            ma_salle.ajouter_seance(nouvelle_seance)

        elif choix == "3":
            print("\n--- RÉSERVER UNE SÉANCE ---")
            id_m = input_securise("ID du membre (ex: MEM-XXXXXX) : ").upper()
            if not id_m: continue
            id_s = input_securise("ID de la séance (ex: SEA-XXXXXX) : ").upper()
            if not id_s: continue

            ma_salle.reserver_seance(id_m, id_s)

        elif choix == "4":
            print("\n--- ANNULER UNE RÉSERVATION ---")
            id_m = input_securise("ID du membre : ").upper()
            if not id_m: continue
            id_s = input_securise("ID de la séance : ").upper()
            if not id_s: continue

            ma_salle.annuler_reservation(id_m, id_s)

        elif choix == "5":
            print("\n--- CALCULER LE TARIF REEL (Polymorphisme) ---")
            id_s = input_securise("ID de la séance : ").upper()
            if not id_s: continue
            id_m = input_securise("ID du membre (pour appliquer une réduction éventuelle) : ").upper()
            if not id_m: continue

            seance = ma_salle.seances.get(id_s)
            membre = ma_salle.membres.get(id_m)

            if not seance or not membre:
                print("❌ Erreur : Séance ou membre introuvable.")
                continue

            tarif_base = seance.calculer_tarif()
            tarif_final = Outils.appliquer_reduction(tarif_base, membre.age)

            print(f"\n--- Détails de tarification ---")
            print(f"• Séance : {seance.nom} ({seance.__class__.__name__})")
            print(f"• Membre : {membre.nom} ({membre.age} ans)")
            print(f"• Tarif de base (calculé selon la formule) : {tarif_base} €")
            if tarif_final < tarif_base:
                print(f"• 🎉 Réduction appliquée pour son âge ! Tarif final : {tarif_final} €")
            else:
                print(f"• Tarif final : {tarif_final} € (Pas de réduction applicable)")

        elif choix == "6":
            print("\n--- RECHERCHE AVANCÉE (Filtres optionnels) ---")
            print("Laissez vide pour ignorer un filtre.")
            f_coach = input("Nom du coach à chercher : ").strip()
            f_type = input("Type de cours (CoursCollectif ou CoachingPersonnel) : ").strip()
            f_dispo_saisie = input("Ne voir que les séances disponibles ? (oui/non) : ").strip().lower()

            filtres = {}
            if f_coach: filtres['coach'] = f_coach
            if f_type: filtres['type_seance'] = f_type
            if f_dispo_saisie in ['oui', 'o', 'y', 'yes']:
                filtres['disponible'] = True
            elif f_dispo_saisie in ['non', 'n', 'no']:
                filtres['disponible'] = False

            resultats = ma_salle.rechercher_avancee(**filtres)
            print(f"\n🔎 {len(resultats)} séance(s) trouvée(s) :")
            for r in resultats:
                print(f" - {r}")

        elif choix == "7":
            print("\n--- RÉSERVATIONS D'UN MEMBRE ---")
            id_m = input_securise("ID du membre : ").upper()
            if not id_m: continue

            membre = ma_salle.membres.get(id_m)
            if not membre:
                print("❌ Erreur : Membre introuvable.")
                continue

            print(f"\n📋 Réservation(s) de {membre.nom} ({len(membre)} active(s)) :")
            if not membre.reservations:
                print("  Aucune réservation en cours.")
            else:
                for s in membre.reservations:
                    print(f" - {s}")

        elif choix == "8":
            ma_salle.afficher_statistiques()

        elif choix == "9":
            print("\n👋 Merci d'avoir utilisé l'application FitZone ! À bientôt.")
            break
        else:
            print("❌ Option invalide. Veuillez entrer un nombre entre 1 et 9.")


if __name__ == "__main__":
    main()