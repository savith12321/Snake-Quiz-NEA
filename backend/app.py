from flask import Flask
from services.snake_service import snake_bp
from services.user_service import user_bp
from services.attempt_service import attempt_bp
from services.meta_service import meta_bp
from services.auth_service import auth_bp
from services.quiz_service import quiz_bp
from services.leaderboard_service import leaderboard_bp
app = Flask(__name__)

# Register services
app.register_blueprint(meta_bp)
app.register_blueprint(snake_bp)
app.register_blueprint(user_bp)
app.register_blueprint(attempt_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(leaderboard_bp)

if __name__ == "__main__":
    app.run(debug=True)