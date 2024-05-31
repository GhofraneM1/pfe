from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/patient_form', methods=['GET', 'POST'])
def patient_form():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        sexe = request.form['sexe']
        date_naissance = request.form['date_naissance']
        adresse = request.form['adresse']
        assurance = request.form['assurance']
        id_social = request.form['id_social']
        poids = request.form['poids']
        taille = request.form['taille']
        imc = request.form['imc']
        # Traiter les données du formulaire ici
        return redirect(url_for('home'))
    return render_template('patient_form.html')

@app.route('/report')
def report():
    # Générer et afficher le rapport
    return render_template('report.html')

if __name__ == '__main__':
    app.run(debug=True)
