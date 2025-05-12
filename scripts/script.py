from faker import Faker
from app1.models import Product

# Initialize Faker instance
fake = Faker('en_IN')  # 'en_IN' is for Indian localization

# List of 60 Indian breakfast items
breakfast_names = [
    'Idli', 'Dosa', 'Poha', 'Paratha', 'Aloo Puri', 'Chole Bhature', 'Upma', 'Puri Bhaji', 
    'Samosa', 'Vada Pav', 'Pav Bhaji', 'Chilla', 'Pongal', 'Sabudana Khichdi', 'Aloo Tikki', 
    'Medu Vada', 'Kachori', 'Thepla', 'Uttapam', 'Rava Kesari', 'Misal Pav', 'Khaman Dhokla', 
    'Farcha', 'Baida Roti', 'Methi Thepla', 'Batata Vada', 'Aloo Gobi Paratha', 'Dhokla', 
    'Gobi Paratha', 'Malai Paratha', 'Aloo Keema Paratha', 'Bhakri', 'Poha with Jalebi', 
    'Bhel Puri', 'Ragda Pattice', 'Sabzi Paratha', 'Kachaudi', 'Moong Dal Chilla', 'Methi Thepla', 
    'Pesarattu', 'Neer Dosa', 'Kesari Bhath', 'Khakra', 'Lassi with Paratha', 'Shrikhand', 
    'Kaladi', 'Kothimbir Vadi', 'Misal Pav', 'Bada Pav', 'Roti with Subzi', 'Puran Poli', 
    'Amritsari Kulcha', 'Pesarattu', 'Batata Poha', 'Thalipeeth', 'Khichu', 'Samosa Chaat', 
    'Sattu Paratha', 'Chutney Sandwich', 'Khichdi'
]

# Function to generate fake products
def generate_fake_products():
    for name in breakfast_names:
        # Generate a fake description
        description = fake.sentence(nb_words=5)  # Creates a random sentence of 10 words
        
        # Create a new Product instance with the generated name and description
        product = Product(
            name=name,
            description=description,
            is_active=True  # You can also use random values for is_active if needed
        )
        product.save()

# Run the function to generate products
generate_fake_products()
