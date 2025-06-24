
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import pickle
import joblib
import pandas as pd

# Load models and encoders
classifier_model = pickle.load(open('classifier.pkl', 'rb'))
fertilizer_model = pickle.load(open('fertilizer.pkl', 'rb'))
crop_model = joblib.load(open('ensemble_crop_model_v1.pkl', 'rb'))
label_encoders = joblib.load(open('label_encoders.pkl', 'rb'))

# Load government schemes
with open('Scheme.json', 'r') as f:
    scheme_data = json.load(f)


class AgroAidGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agro Aid - Unified Chatbot")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')

        self.bot = AgroAidBot()
        self.bot.display_message = self.display_bot_message  # Redirect bot output to GUI

        self.setup_gui()

    def setup_gui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background='#1a1a1a')
        style.configure('Dark.TButton', background='#444444', foreground='white', padding=8)
        style.map('Dark.TButton', background=[('active', '#666666')])
        style.configure('Input.TEntry', fieldbackground='#333333', foreground='white', insertcolor='white')

        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, width=70, height=20,
            font=('Arial', 11), bg='#1a1a1a', fg='white', insertbackground='white'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_display.tag_configure('bot', foreground='#00ff00', font=('Arial', 11, 'bold'))
        self.chat_display.tag_configure('user', foreground='#ffffff')

        # Input frame with entry and send button
        input_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.input_field = ttk.Entry(input_frame, font=('Arial', 11), style='Input.TEntry')
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind('<Return>', lambda e: self.send_message())

        send_button = ttk.Button(input_frame, text="Send", style='Dark.TButton', command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        # Quick option buttons
        options_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        options_frame.pack(fill=tk.X)

        options = [
            ("Crop Prediction", "1"),
            ("Fertilizer Recommendation", "2"),
            ("Disease Detection", "3"),
            ("Gov. Schemes", "4")
        ]

        for text, value in options:
            btn = ttk.Button(
                options_frame, text=text, style='Dark.TButton',
                command=lambda v=value: self.quick_option(v)
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Initial greetings and instructions
        self.display_bot_message("Hello! I am Agro Aid. How can I help you today?\n")
        self.display_bot_message(
            "Please choose an option:\n"
            "1) Crop prediction\n"
            "2) Fertilizer recommendation\n"
            "3) Disease detection on plant\n"
            "4) Government scheme suggestion\n"
            "Type 'quit' to exit"
        )

    def display_bot_message(self, message):
        self.chat_display.insert(tk.END, f"🤖 Bot: {message}\n", 'bot')
        self.chat_display.see(tk.END)

    def display_user_message(self, message):
        self.chat_display.insert(tk.END, f"👤 You: {message}\n", 'user')
        self.chat_display.see(tk.END)

    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.display_user_message(message)
            if message.lower() == 'quit':
                self.display_bot_message("Goodbye! 👋")
                self.root.after(1000, self.root.destroy)
                return
            self.bot.process_input(message)

    def quick_option(self, option):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, option)
        self.send_message()

    def run(self):
        self.root.mainloop()


class AgroAidBot:
    def __init__(self):
        self.state = 'main_menu'
        self.inputs = {}
        self.step_index = 0
        self.display_message = print  # Placeholder, redirected by GUI

        # Department and scheme data
        self.dept_list = scheme_data.get('departments', [])
        self.selected_dept = None

        # Inputs order for crop prediction
        self.crop_steps = [
            'Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity',
            'pH_Value', 'Rainfall', 'Soil_Type', 'Variety'
        ]

        # Inputs order for fertilizer recommendation
        self.ferti_steps = [
            'Temperature', 'Humidity', 'Moisture', 'Soil_Type', 'Crop', 'Nitrogen', 'Potassium', 'Phosphorus'
        ]

    def process_input(self, message):
        if self.state == 'main_menu':
            if message == '1':
                self.state = 'crop_prediction'
                self.step_index = 0
                self.inputs.clear()
                self.display_message("You've selected Crop Prediction.")
                self.display_message(f"Please enter {self.crop_steps[self.step_index]}:")
            elif message == '2':
                self.state = 'fertilizer_start'
                self.step_index = 0
                self.inputs.clear()
                self.display_message("You've selected Fertilizer Recommendation.")
                self.display_message(f"Please enter {self.ferti_steps[self.step_index]}:")
            elif message == '3':
                self.display_message("🦠 Disease detection module coming soon.")
            elif message == '4':
                self.state = 'select_dept'
                self.display_message("📜 Available Departments:")
                for i, dept in enumerate(self.dept_list, 1):
                    self.display_message(f"{i}. {dept['deptName']}")
                self.display_message("Enter the department number:")
            else:
                self.display_message("❌ Invalid option. Please choose between 1-4.")

        elif self.state == 'crop_prediction':
            if self.step_index < len(self.crop_steps):
                key = self.crop_steps[self.step_index]
                self.inputs[key] = message
                self.step_index += 1
                if self.step_index < len(self.crop_steps):
                    self.display_message(f"Please enter {self.crop_steps[self.step_index]}:")
                else:
                    self.run_crop_prediction()
                    self.state = 'main_menu'
                    self.display_message("\nBack to main menu. Please choose an option:")

        elif self.state == 'fertilizer_start':
            if self.step_index < len(self.ferti_steps):
                key = self.ferti_steps[self.step_index]
                self.inputs[key] = message
                self.step_index += 1
                if self.step_index < len(self.ferti_steps):
                    self.display_message(f"Please enter {self.ferti_steps[self.step_index]}:")
                else:
                    self.run_fertilizer_prediction()
                    self.state = 'main_menu'
                    self.display_message("\nBack to main menu. Please choose an option:")

        elif self.state == 'select_dept':
            try:
                index = int(message) - 1
                if 0 <= index < len(self.dept_list):
                    self.selected_dept = self.dept_list[index]
                    self.state = 'select_scheme'
                    self.display_message(f"Schemes under {self.selected_dept['deptName']}:")
                    for i, scheme in enumerate(self.selected_dept.get('schemes', []), 1):
                        self.display_message(f"{i}. {scheme['schemeName']}")
                    self.display_message("Enter the scheme number:")
                else:
                    self.display_message("Invalid department number.")
            except ValueError:
                self.display_message("Please enter a valid number.")

        elif self.state == 'select_scheme':
            try:
                index = int(message) - 1
                schemes = self.selected_dept.get('schemes', [])
                if 0 <= index < len(schemes):
                    scheme = schemes[index]
                    self.state = 'main_menu'
                    self.display_scheme_details(scheme)
                    self.display_message("\nBack to main menu. Please choose an option:")
                else:
                    self.display_message("Invalid scheme number.")
            except ValueError:
                self.display_message("Please enter a valid number.")

    def display_scheme_details(self, scheme):
        self.display_message(f"\n📋 Scheme: {scheme['schemeName']}")
        for input_type in scheme.get('inputTypes', []):
            self.display_message(f"\n🔸 {input_type['inputTypeName']}")
            details = input_type.get('details', {})
            self.display_message(f"  Description: {details.get('schemeDescription', 'N/A')}")
            self.display_message(f"  Subsidy: {details.get('subsidy', 'N/A')}")
            self.display_message(f"  Eligibility: {details.get('Eligibility', 'N/A')}")
            self.display_message("  Required Documents:")
            for doc in details.get('documentsRequired', []):
                self.display_message(f"    - {doc}")

    def run_crop_prediction(self):
        try:
            # Convert numeric inputs to float
            for key in ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH_Value', 'Rainfall']:
                self.inputs[key] = float(self.inputs[key])

            # Encode categorical inputs using label encoders
            encoded = self.inputs.copy()
            encoded['Soil_Type'] = label_encoders['Soil_Type'].transform([self.inputs['Soil_Type']])[0]
            encoded['Variety'] = label_encoders['Variety'].transform([self.inputs['Variety']])[0]

            df = pd.DataFrame([encoded])
            crop_code = crop_model.predict(df)[0]
            crop_name = label_encoders['Crop'].inverse_transform([crop_code])[0]

            self.display_message(f"✅ Predicted Crop: {crop_name}")
            self.display_message(f"🌾 Variety: {self.inputs['Variety']}")
        except Exception as e:
            self.display_message(f"❌ Error during crop prediction: {str(e)}")

    def run_fertilizer_prediction(self):
        try:
            # Convert numeric inputs to float
            for key in ['Temperature', 'Humidity', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorus']:
                self.inputs[key] = float(self.inputs[key])

            # Encode categorical inputs using label encoders
            soil_encoded = label_encoders['Soil_Type'].transform([self.inputs['Soil_Type']])[0]
            crop_encoded = label_encoders['Crop'].transform([self.inputs['Crop']])[0]

            # Prepare input array for classifier
            fert_input = [
                int(self.inputs['Temperature']),
                int(self.inputs['Humidity']),
                int(self.inputs['Moisture']),
                soil_encoded,
                crop_encoded,
                int(self.inputs['Nitrogen']),
                int(self.inputs['Potassium']),
                int(self.inputs['Phosphorus'])
            ]

            pred_class_index = classifier_model.predict([fert_input])[0]

            # fertilizer_model.classes_ contains classes; pred_class_index is an integer label predicted by classifier_model
            # So to get fertilizer name, we can just map pred_class_index directly, assuming fertilizer_model.classes_ is array of fertilizer names
            fert_classes = fertilizer_model.classes_
            if hasattr(fertilizer_model, 'classes_'):
                fert_classes = fertilizer_model.classes_
            else:
                # fallback, if fertilizer_model is not a classifier but list of fertilizer names
                fert_classes = [str(i) for i in range(10)]

            if 0 <= pred_class_index < len(fert_classes):
                fert_result = fert_classes[pred_class_index]
            else:
                fert_result = str(pred_class_index)  # fallback

            self.display_message(f"💡 Recommended Fertilizer: {fert_result}")
        except Exception as e:
            self.display_message(f"❌ Error during fertilizer recommendation: {str(e)}")


if __name__ == '__main__':
    AgroAidGUI().run()
