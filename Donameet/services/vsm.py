from Donameet.models import db, User, Request
from geopy.distance import vincenty


# Urutan kolom: username, A, B, AB, O, Rh+, Rh-, Lat, Lng
class VSM:
    class __VSM:
        def __init__(self):
            self.users = []
            self.patients = []

            users = User.query().all()
            for user in users:
                add_donor(user)

            patients = Request.query().filter_by(is_fulfilled=False).all()
            for patient in patient:
                add_patient(patient)

        def add_donor(self, donor):
            blood_type = {
                'A': [100, 0, 10, 0],
                'B': [0, 100, 10, 0],
                'AB': [0, 0, 100, 0],
                'O': [10, 10, 10, 100],
                '+': [30, 0],
                '-': [10, 30]
            }

            tmp = [donor.username]
            tmp.extend(blood_type[donor.blood_type])
            tmp.extend(blood_type[donor.rhesus])
            tmp.extend([donor.lat, donor.lng])

            self.users.append(tmp)

        def add_patient(self, patient):
            blood_type = {
                'A': [1, 0, 0, 0],
                'B': [0, 1, 0, 0],
                'AB': [0, 0, 1, 0],
                'O': [0, 0, 0, 1],
                '+': [1, 0],
                '-': [0, 1]
            }

            tmp = [donor.username]
            tmp.extend(blood_type[donor.blood_type])
            tmp.extend(blood_type[donor.rhesus])
            tmp.extend([donor.lat, donor.lng])

            self.patients.append(tmp)

        def find_donor(self, patient):
            vectors = []
            patient_pos = (patient[7], patient[8])
            patient_norm = 0

            for i in range(1, 7):
                patient_norm += patient[i] * patient[i]

            patient_norm = (patient_norm + 1) ** 0.5  # 1 for distance column

            for user in self.users:
                dot = 0
                donor_norm = 0

                for i in range(1, 7):
                    dot += patient[i] * user[i]
                    donor_norm += user[i] * user[i]

                donor_norm = donor_norm ** 0.5

                donor_pos = (user[7], user[8])
                if user[7] != 0 or user[8] != 0:
                    dot += 10 / (1 + vincenty(patient_pos, donor_pos)**2)

                cosine_similarity = dot / (patient_norm * donor_norm)

                vectors.append({'username': user.username, 'similarity': cosine_similarity})

            return sorted(vectors, key=lambda k: k['similarity'], reverse=True)[5:]

    instance = None

    def __new__(cls):
        if not VSM.instance:
            VSM.instance = VSM.__VSM()

        return VSM.instance

    @staticmethod
    def create_patient_mismatch_filter(patient):
        def mismatch_filter(entry):
            donor = User.query().filter_by(username = entry['username'])
            if patient.rhesus == '-' and donor.rhesus:
                return False
            elif patient.blood_type != donor.blood_type:
                blood_index = {
                    'A': 0,
                    'B': 1,
                    'AB': 2,
                    'O': 3,
                }

                donor_compatibility = [ # A_i,j: i can donor to j
                    [1, 0, 1, 0],
                    [0, 1, 1, 0],
                    [0, 0, 1, 0],
                    [1, 1, 1, 1], 
                ]

                if donor_compatibility \
                    [blood_index[donor.blood_type]] \
                    [blood_index[patient.blood_type]] == 0:
                    return False

            return True

        return mismatch_filter



    @classmethod
    def update(cls, update_type):
        if update_type == 'donor':
            instance.add_donor(User.query().order_by(User.created_at.desc()).first())
        else: # update_type == 'patient'
            patient = Request.query().order_by(Request.created_at.desc()).first()
            result = instance.find_donor(patient)
            result = filter(create_patient_mismatch_filter(patient), result)
            if not result:
                db.session.delete(patient)
                db.session.commit()
                db.session.flush()
                db.session.close()

            return result
