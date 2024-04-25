from app import create_app

# Create the Flask app instance
app = create_app('HarmonyHub')

if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True)
