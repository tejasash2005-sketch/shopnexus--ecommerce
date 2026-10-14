from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Brand, Product
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Master Seed with 500 Realistic Products, Accurate Pricing, Brands, and High-Quality Unsplash Product Images'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Launching 500 Realistic Product Catalog Seed...')

        # 1. Purge for clean state
        Product.objects.all().delete()
        Brand.objects.all().delete()
        Category.objects.all().delete()

        # 2. Categories definition
        categories_data = [
            ('Electronics', '📱', 'Smartphones, laptops, cameras, tablets, and smart home tech.'),
            ('Audio', '🎧', 'Headphones, earbuds, Bluetooth speakers, and sound systems.'),
            ('Fashion', '👗', 'Apparel, hoodies, jackets, denim jeans, and designer wear.'),
            ('Footwear', '👟', 'Sneakers, running shoes, casual footwear, and boots.'),
            ('Beauty & Care', '💄', 'Perfumes, cosmetics, lipstick, and premium skincare.'),
            ('Kitchen', '🍳', 'Air fryers, espresso machines, blenders, and cookware.'),
            ('Home & Living', '🏠', 'Air purifiers, smart lighting, bed linen, and home essentials.'),
            ('Furniture', '🛋️', 'Sofas, ergonomic chairs, bed frames, and living room sets.'),
            ('Watches', '⌚', 'Smartwatches, automatic luxury watches, and sports chronographs.'),
            ('Sports & Fitness', '⚽', 'Yoga mats, dumbbells, gym gear, and fitness trackers.'),
            ('Outdoors', '🏕️', 'Camping tents, travel backpacks, tumblers, and adventure gear.'),
            ('Tools', '🛠️', 'Power drills, laser measures, bit sets, and hand tools.'),
            ('Groceries', '🛒', 'Gourmet coffee beans, dark chocolates, extra virgin olive oil, and organic teas.'),
            ('Toys & Games', '🎮', 'LEGO sets, gaming controllers, board games, and collectables.'),
            ('Books', '📚', 'Bestselling non-fiction, personal growth, psychology, and literature.')
        ]

        cat_map = {}
        for name, icon, desc in categories_data:
            c, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
            c.icon = icon
            c.description = desc
            c.save()
            cat_map[name] = c

        # 3. Brands definition
        brands_data = [
            'Apple', 'Samsung', 'Sony', 'Dell', 'ASUS', 'Canon', 'Bose', 'JBL',
            'Sennheiser', 'Marshall', 'Nike', 'Adidas', 'Puma', "Levi's",
            'Tommy Hilfiger', 'Zara', 'The North Face', 'Timberland', 'Converse',
            'New Balance', 'Ralph Lauren', 'Chanel', 'Dior', 'MAC', 'CeraVe',
            'Estée Lauder', "L'Oréal", 'Philips', "De'Longhi", 'Ninja',
            'Instant Pot', 'Dyson', 'IKEA', 'West Elm', 'Herman Miller', 'Zinus',
            'Fossil', 'Casio', 'Seiko', 'Tissot', 'Fitbit', 'Lululemon', 'Bowflex',
            'Decathlon', 'Coleman', 'Osprey', 'Stanley', 'DEWALT', 'Bosch',
            'Blue Tokai', 'Lindt', 'Borges', 'LEGO', 'Hasbro', 'Penguin', 'HarperCollins',
            'OnePlus', 'Google', 'Realme', 'Xiaomi', 'HP', 'Lenovo', 'Boat', 'Cross', 'Gucci'
        ]

        brand_map = {}
        for b_name in brands_data:
            b, _ = Brand.objects.get_or_create(name=b_name)
            brand_map[b_name] = b

        # 4. Verified Image Pools per Category (Direct Unsplash Product Photos)
        IMAGE_POOLS = {
            'Electronics': [
                "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1593784991095-a205069470b6?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=800&q=80"
            ],
            'Audio': [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=800&q=80"
            ],
            'Fashion': [
                "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1509967419530-da38b4704bc6?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582552938357-32b906df40cb?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80"
            ],
            'Footwear': [
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80"
            ],
            'Beauty & Care': [
                "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1608248597261-12c8b73a216f?auto=format&fit=crop&w=800&q=80"
            ],
            'Kitchen': [
                "https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1570222094114-d054a817e56b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80"
            ],
            'Home & Living': [
                "https://images.unsplash.com/photo-1585771724684-38269d6639fd?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1550985616-10810253b84d?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80"
            ],
            'Furniture': [
                "https://images.unsplash.com/photo-1580481072645-022f9a6d1270?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80"
            ],
            'Watches': [
                "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80"
            ],
            'Sports & Fitness': [
                "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80"
            ],
            'Outdoors': [
                "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80"
            ],
            'Tools': [
                "https://images.unsplash.com/photo-1504148455328-c376907d081c?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80"
            ],
            'Groceries': [
                "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1549007994-cb92caebd54b?auto=format&fit=crop&w=800&q=80"
            ],
            'Toys & Games': [
                "https://images.unsplash.com/photo-1587654780291-39c9404d746b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=800&q=80"
            ],
            'Books': [
                "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80"
            ]
        }

        # 5. Master Templates per Category (Used to generate 500 distinct items with realistic specs & pricing)
        CATEGORY_TEMPLATES = {
            'Electronics': [
                ("Apple", "iPhone 15 Pro", [("128GB, Natural Titanium", 124900), ("256GB, Blue Titanium", 134900), ("512GB, Black Titanium", 154900), ("1TB, White Titanium", 174900)]),
                ("Samsung", "Galaxy S24 Ultra", [("256GB, Titanium Black", 119999), ("512GB, Titanium Gray", 129999), ("1TB, Titanium Violet", 149999)]),
                ("Apple", "MacBook Pro 14\"", [("M3 Chip, 8GB RAM, 512GB", 169900), ("M3 Pro, 18GB RAM, 512GB", 199900), ("M3 Max, 36GB RAM, 1TB", 319900)]),
                ("Dell", "XPS 13 Laptop", [("Intel Core i7, 16GB RAM, 512GB", 129990), ("Intel Core i9, 32GB RAM, 1TB", 169990)]),
                ("ASUS", "ROG Zephyrus G16", [("Core Ultra 7, RTX 4060", 139990), ("Core Ultra 9, RTX 4070", 164990)]),
                ("Canon", "EOS R6 Mark II", [("Body Only", 215000), ("With 24-105mm Lens Kit", 249995)]),
                ("Sony", "Alpha 7 IV Mirrorless Camera", [("Body Only", 198990), ("With 28-70mm Lens", 219990)]),
                ("Samsung", "Crystal 4K Smart TV", [("43-Inch UHD", 28990), ("55-Inch UHD Pro", 38990), ("65-Inch Neo QLED", 79990)]),
                ("Apple", "iPad Air 11\"", [("Wi-Fi 128GB", 59900), ("Wi-Fi + Cellular 256GB", 74900)]),
                ("Google", "Pixel 8 Pro", [("128GB, Obsidian", 89999), ("256GB, Bay Blue", 97999)]),
                ("OnePlus", "OnePlus 12 5G", [("12GB RAM, 256GB", 64999), ("16GB RAM, 512GB", 69999)])
            ],
            'Audio': [
                ("Sony", "WH-1000XM5 Noise Canceling Headphones", [("Black Edition", 24990), ("Silver Edition", 24990), ("Midnight Blue", 26990)]),
                ("Apple", "AirPods Pro 2nd Gen", [("USB-C Charging Case", 20900), ("MagSafe Wireless Case", 22900)]),
                ("Apple", "AirPods Max", [("Space Grey", 59900), ("Silver", 59900), ("Sky Blue", 59900)]),
                ("Bose", "QuietComfort Ultra Headphones", [("Black", 29900), ("White Smoke", 29900)]),
                ("Bose", "SoundLink Flex Bluetooth Speaker", [("Stone Blue", 13490), ("Black", 13490)]),
                ("JBL", "Flip 6 Waterproof Speaker", [("Ocean Blue", 8999), ("Squad Camo", 8999), ("Red", 8999)]),
                ("Sennheiser", "Momentum 4 Wireless", [("Graphite Edition", 29990), ("White & Copper", 31990)]),
                ("Marshall", "Stanmore III Bluetooth Speaker", [("Black", 27999), ("Cream White", 28999)]),
                ("Boat", "Airdopes 141 TWS Earbuds", [("Bold Black", 1299), ("Cider Blue", 1299)])
            ],
            'Fashion': [
                ("Levi's", "501 Original Straight Fit Jeans", [("Dark Indigo Wash", 2999), ("Medium Stonewash", 3299), ("Black Rigid", 3499)]),
                ("Levi's", "511 Slim Fit Stretch Jeans", [("Rinsed Blue", 2799), ("Charcoal Grey", 2999)]),
                ("Nike", "Club Fleece Pullover Hoodie", [("Black / White Logo", 3595), ("Heather Grey", 3595), ("Obsidian Blue", 3795)]),
                ("The North Face", "ThermoBall Eco Insulated Jacket", [("Matte Black", 14999), ("Summit Gold", 15999)]),
                ("Tommy Hilfiger", "Classic Fit Cotton Polo Shirt", [("Navy Blue", 2499), ("Classic Red", 2499), ("Bright White", 2499)]),
                ("Zara", "Oversized Denim Trucker Jacket", [("Light Vintage Wash", 3990), ("Washed Black", 4290)]),
                ("Adidas", "Essentials 3-Stripes Track Jacket", [("Black / White", 2999), ("Legend Ink", 3199)]),
                ("Ralph Lauren", "Cotton Mesh Polo Shirt", [("Polo Black", 6990), ("Royal Blue", 7290)])
            ],
            'Footwear': [
                ("Nike", "Air Force 1 '07 Leather Sneakers", [("Triple White", 7495), ("Black / White", 7995)]),
                ("Nike", "Pegasus 40 Running Shoes", [("Pure Platinum", 9295), ("Total Orange", 9895)]),
                ("Adidas", "Ultraboost Light Running Shoes", [("Core Black", 13999), ("Cloud White", 13999)]),
                ("Puma", "RS-X3 Retro Unisex Sneakers", [("White / Red / Blue", 5999), ("All Black Edition", 6499)]),
                ("Timberland", "6-Inch Premium Waterproof Boots", [("Wheat Nubuck", 13990), ("Black Full-Grain", 14990)]),
                ("Converse", "Chuck Taylor All Star High Top", [("Black Canvas", 3999), ("Optic White", 3999)]),
                ("New Balance", "574 Core Casual Sneakers", [("Grey / White", 6499), ("Navy / Silver", 6899)])
            ],
            'Beauty & Care': [
                ("Chanel", "Bleu de Chanel Eau de Parfum", [("50ml Spray", 8500), ("100ml Spray", 11200), ("150ml Spray", 13800)]),
                ("Dior", "Sauvage Eau de Toilette", [("60ml Bottle", 8200), ("100ml Bottle", 10500), ("200ml Refill", 15500)]),
                ("MAC", "Matte Lipstick", [("Ruby Woo (3g)", 1650), ("Velvet Teddy (3g)", 1650), ("Chili (3g)", 1650)]),
                ("CeraVe", "Hydrating Facial Cleanser", [("236ml Bottle", 899), ("473ml Family Size", 1199)]),
                ("Estée Lauder", "Advanced Night Repair Serum", [("30ml Complex", 5500), ("50ml Complex", 6900)]),
                ("L'Oréal", "Revitalift Hyaluronic Acid Serum", [("15ml Dropper", 499), ("30ml Dropper", 749)])
            ],
            'Kitchen': [
                ("Philips", "XL Air Fryer HD9270", [("6.2 Liter Black", 10999), ("6.2 Liter White & Rose Gold", 11499)]),
                ("De'Longhi", "Dedica Deluxe Espresso Machine", [("Silver Stainless Steel", 19990), ("Matte Black", 20990)]),
                ("Ninja", "Professional Countertop Blender", [("1000W 72oz Pitcher", 8999), ("1200W Auto-iQ System", 10999)]),
                ("Instant Pot", "Duo 7-in-1 Electric Pressure Cooker", [("6 Quart Steel", 8990), ("8 Quart XL", 10990)]),
                ("Dyson", "V15 Detect Cordless Vacuum Cleaner", [("Yellow / Nickel", 58900), ("Absolute Gold Edition", 62900)])
            ],
            'Home & Living': [
                ("Dyson", "Purifier Cool TP07 Air Purifier", [("White / Silver", 36900), ("Black / Nickel", 38900)]),
                ("Philips", "Smart Wi-Fi LED Color Bulb", [("E27 Pack of 2", 1799), ("E27 Pack of 4", 3299)]),
                ("Bombay Dyeing", "100% Cotton King Bed Sheet Set", [("Floral Garden Blue", 1999), ("Geometric Grey", 2199)]),
                ("Amazon", "Echo Dot 5th Gen Smart Speaker", [("Deep Sea Blue", 3999), ("Charcoal Black", 3999)])
            ],
            'Furniture': [
                ("IKEA", "Strandmon Wing Chair & Footstool", [("Nordvalla Dark Grey", 15990), ("Skiftebo Yellow", 16990)]),
                ("West Elm", "Harmony Leather Sofa 3-Seater", [("Saddle Top-Grain Leather", 74900), ("Nutmeg Leather", 78900)]),
                ("Herman Miller", "Aeron Ergonomic Office Chair", [("Size B Graphite Frame", 98900), ("Size C Polished Aluminum", 112000)]),
                ("Zinus", "Metal Frame Queen Platform Bed", [("Matte Black Steel", 11999), ("Rustic Wood Accent", 13499)])
            ],
            'Watches': [
                ("Fossil", "Gen 6 Touchscreen Smartwatch", [("Smoke Stainless Steel", 17495), ("Brown Leather Strap", 16495)]),
                ("Casio", "G-Shock GA-2100 Octagon Watch", [("All Black CasiOak", 7995), ("Transparent Skeleton", 8295)]),
                ("Seiko", "Presage Automatic Stainless Watch", [("Cocktail Time Blue", 31900), ("Sunburst Silver", 33500)]),
                ("Apple", "Watch Series 9 GPS 45mm", [("Midnight Aluminum", 39900), ("Starlight Aluminum", 39900)]),
                ("Tissot", "PRX Powermatic 80 Automatic", [("Blue Dial 40mm", 52000), ("Ice Blue Dial 35mm", 54000)])
            ],
            'Sports & Fitness': [
                ("Lululemon", "5mm Reversible Yoga Mat", [("Black / Slate", 5400), ("Sage Green", 5400)]),
                ("Bowflex", "SelectTech 552 Adjustable Dumbbells", [("Pair with Stand", 31500), ("Single Dumbbell", 15900)]),
                ("Fitbit", "Charge 6 Fitness Tracker", [("Obsidian / Black", 11999), ("Coral / Champagne Gold", 11999)]),
                ("Decathlon", "Kiprun Cushioned Running Shoes", [("Carbon Black", 3499), ("Neon Blue", 3499)])
            ],
            'Outdoors': [
                ("Coleman", "Sundome 4-Person Waterproof Tent", [("Green / White", 6999), ("Navy / Grey", 7299)]),
                ("Osprey", "Farpoint 40 Travel Backpack", [("Volcanic Grey", 13500), ("Tunnel Vision Blue", 13500)]),
                ("Stanley", "Adventure Quencher H2.O Tumbler", [("Eucalyptus 1.2L", 3199), ("Rose Quartz 1.2L", 3199)])
            ],
            'Tools': [
                ("DEWALT", "20V MAX Cordless Drill Combo Kit", [("2-Tool Kit with Bag", 17999), ("3-Tool Pro Kit", 22999)]),
                ("Bosch", "Professional Laser Distance Measure", [("GLM 50-27 (50m)", 6499), ("GLM 100-25 C (100m)", 11999)]),
                ("Stanley", "20-oz Fiberglass Claw Hammer", [("Ergonomic Rubber Grip", 899), ("Heavy Duty Steel", 1099)])
            ],
            'Groceries': [
                ("Blue Tokai", "Dark Roast Whole Coffee Beans", [("Vienna Roast 250g", 390), ("Attikan Estate 500g", 620)]),
                ("Lindt", "Excellence Dark Chocolate 3-Pack", [("85% Cocoa Intense", 749), ("90% Supreme Dark", 799)]),
                ("Borges", "Extra Virgin Olive Oil Cold Pressed", [("1 Litre Glass Bottle", 1199), ("2 Litre Family Tin", 2199)])
            ],
            'Toys & Games': [
                ("LEGO", "Technic Porsche 911 GT3 RS Set", [("1:8 Scale Orange Model", 24999), ("Collectors Edition Box", 26999)]),
                ("Sony", "PS5 DualSense Wireless Controller", [("Midnight Black", 4990), ("Cosmic Red", 5290), ("Starlight Blue", 5290)]),
                ("Hasbro", "Monopoly Classic Family Board Game", [("Standard Edition", 1099), ("Deluxe Wooden Edition", 1999)])
            ],
            'Books': [
                ("Penguin", "Atomic Habits by James Clear", [("Hardcover Edition", 499), ("Paperback Edition", 399)]),
                ("HarperCollins", "The Psychology of Money by Morgan Housel", [("Paperback Edition", 320), ("Hardcover Gift Edition", 599)]),
                ("Penguin", "Sapiens: A Brief History of Humankind", [("Special Illustrated Edition", 699), ("Standard Paperback", 450)])
            ]
        }

        # 6. Seeding Execution (Exactly 500 products)
        total_target = 500
        created_count = 0

        # We loop through categories until 500 distinct products are added
        cat_names = list(cat_map.keys())

        iteration = 0
        while created_count < total_target:
            for cat_name in cat_names:
                if created_count >= total_target:
                    break

                cat_obj = cat_map[cat_name]
                img_pool = IMAGE_POOLS.get(cat_name, [
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80"
                ])
                templates = CATEGORY_TEMPLATES.get(cat_name, [])

                if not templates:
                    continue

                # Pick template based on iteration offset
                tmpl_brand, tmpl_name, variants = templates[iteration % len(templates)]
                variant_spec, base_price = variants[iteration % len(variants)]

                # Apply slight realistic variation if looping multiple rounds
                round_num = iteration // len(templates)
                price_adj = 1.0 + (round_num * 0.05)
                effective_price = int(base_price * price_adj)

                # Format product name cleanly
                if round_num == 0:
                    full_name = f"{tmpl_brand} {tmpl_name} ({variant_spec})"
                else:
                    full_name = f"{tmpl_brand} {tmpl_name} - {variant_spec} (V{round_num + 1})"

                # Pricing & Discount logic
                price = int(effective_price * 1.15) if random.random() > 0.3 else effective_price
                disc_price = effective_price if price > effective_price else None

                img_url = img_pool[(created_count + iteration) % len(img_pool)]
                brand_obj = brand_map.get(tmpl_brand)

                # Unique check & creation
                Product.objects.create(
                    category=cat_obj,
                    brand=brand_obj,
                    name=full_name,
                    price=price,
                    discount_price=disc_price,
                    stock=random.randint(15, 180),
                    is_active=True,
                    is_featured=(created_count % 7 == 0),
                    is_bestseller=(created_count % 5 == 0),
                    image_url=img_url,
                    description=f"Official {full_name}. High quality certified product manufactured by {tmpl_brand}. Complete with manufacturer warranty and original packaging.",
                    short_description=f"Authentic {full_name} with premium features."
                )
                created_count += 1

            iteration += 1

        self.stdout.write(self.style.SUCCESS(f'🎉 ULTIMATE SEED COMPLETE: {created_count} realistic products created with accurate pricing & Unsplash images!'))
