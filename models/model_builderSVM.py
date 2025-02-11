from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib

iris = load_iris()
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = SVC(kernel='rbf', probability=True)
model.fit(X_train, y_train)

joblib.dump(model, "models/iris_modelSVM.pkl")

print("Modèle entraîné et sauvegardé sous 'iris_modelSVM.pkl'")