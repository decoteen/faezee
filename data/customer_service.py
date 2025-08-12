#!/usr/bin/env python3
"""
Customer Service and Authentication
Manages customer database and authentication.
"""

from typing import Optional, Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CustomerService:
    """Customer service management class"""
    
    def __init__(self):
        # Customer database with authentic customer codes from original data
        self.customers = {
            # کدهای مشتری شش رقمی طبق فایل اصلی
            "000001": {"customer_id": "000001", "name": "خانم نیلوفر صفرپور", "city": "اردبیل"},
            "000002": {"customer_id": "000002", "name": "خانم اعظم افرایی", "city": "اصفهان"},
            "000003": {"customer_id": "000003", "name": "آقای مجید زین العابدین", "city": "اصفهان"},
            "000004": {"customer_id": "000004", "name": "آقای روح الله شاکریان", "city": "کاشان"},
            "000005": {"customer_id": "000005", "name": "آقای یاشار حیدری", "city": "مطهری کرج"},
            "000006": {"customer_id": "000006", "name": "آقای شاهوی امیری", "city": "کرج"},
            "000007": {"customer_id": "000007", "name": "آقای مرتضی انجیله ای", "city": "دشت بهشت کرج"},
            "000008": {"customer_id": "000008", "name": "آقای جواد رشیدی", "city": "اکومال کرج"},
            "000009": {"customer_id": "000009", "name": "خانم مژگان جعفری", "city": "کاج کرج"},
            "000010": {"customer_id": "000010", "name": "آقای سینا اسد اللهی", "city": "رستاخیز"},
            "000011": {"customer_id": "000011", "name": "خانم ندا اکبری", "city": "تبریز"},
            "000012": {"customer_id": "000012", "name": "آقای ایمان کوهگرد", "city": "تبریز"},
            "000013": {"customer_id": "000013", "name": "آقای بهروز توفیقی", "city": "میانه"},
            "000014": {"customer_id": "000014", "name": "آقای یعقوب عبداللهی", "city": "ارومیه"},
            "000015": {"customer_id": "000015", "name": "آقای امیر شمامی", "city": "بوکان"},
            "000016": {"customer_id": "000016", "name": "آقای حسین شفقی", "city": "خوی"},
            "000017": {"customer_id": "000017", "name": "خانم شهربانو فولادی", "city": "بوشهر"},
            "000018": {"customer_id": "000018", "name": "آقای امین گودرزی", "city": "بندرگناوه"},
            "000019": {"customer_id": "000019", "name": "آقای سیدعلی حسین زاده", "city": "شهرجم"},
            "000020": {"customer_id": "000020", "name": "آقای سعید صالحی", "city": "جامی تهران"},
            "000021": {"customer_id": "000021", "name": "آقای مجید رحیمی", "city": "خلیج فارس تهران"},
            "000022": {"customer_id": "000022", "name": "آقای امین کوهزاد", "city": "کاسپین تهران"},
            "000023": {"customer_id": "000023", "name": "آقای وحید صادقی", "city": "دلاوران تهران"},
            "000024": {"customer_id": "000024", "name": "آقای اکوان", "city": "چهاردانگه تهران"},
            "000025": {"customer_id": "000025", "name": "آقای محمد اسداللهی", "city": "ورامین"},
            "000026": {"customer_id": "000026", "name": "آقای سعیدی", "city": "ایرانمال تهران"},
            "000027": {"customer_id": "000027", "name": "آقای مرتضی رمضانی", "city": "جاجرود تهران"},
            "000028": {"customer_id": "000028", "name": "آقای فرزاد رجب زاده", "city": "بجنورد"},
            "000029": {"customer_id": "000029", "name": "آقای مهدی باقر نژاد", "city": "تربت حیدریه"},
            "000030": {"customer_id": "000030", "name": "آقای کاوه مددیان", "city": "مشهد"},
            "000031": {"customer_id": "000031", "name": "آقای محسن اصغری", "city": "بیرجند"},
            "000032": {"customer_id": "000032", "name": "آقای مسعود مهر ابادی", "city": "سبزوار"},
            "000033": {"customer_id": "000033", "name": "آقای حمید رضا علیزاده", "city": "شهرفردوس"},
            "000034": {"customer_id": "000034", "name": "آقای مهدی کشاورز", "city": "اپادانا اهواز"},
            "000035": {"customer_id": "000035", "name": "آقای فرشاد کامران فر", "city": "اهواز"},
            "000036": {"customer_id": "000036", "name": "آقای اسد الله فلاحی", "city": "بندر ماهشهر"},
            "000037": {"customer_id": "000037", "name": "آقای محسن مروج", "city": "بهبهان"},
            "000038": {"customer_id": "000038", "name": "خانم غزاله گلچین", "city": "دزفول"},
            "000039": {"customer_id": "000039", "name": "آقای ابراهیم حسین زاده", "city": "اندیمشک"},
            "000040": {"customer_id": "000040", "name": "آقای محمد کرد", "city": "شوش دانیال"},
            "000041": {"customer_id": "000041", "name": "خانم مریم احمدخانی", "city": "ابهر"},
            "000042": {"customer_id": "000042", "name": "آقای رضا آربونی", "city": "زنجان"},
            "000043": {"customer_id": "000043", "name": "آقای رضا کیفری", "city": "گرمسار"},
            "000044": {"customer_id": "000044", "name": "آقای امین سرابندی", "city": "زاهدان"},
            "000045": {"customer_id": "000045", "name": "خانم مریم ترشیزی", "city": "زاهدان"},
            "000046": {"customer_id": "000046", "name": "آقای علی رئیسی", "city": "شهرکرد"},
            "000047": {"customer_id": "000047", "name": "آقای ایمان آهی تبار", "city": "آمل وبابل"},
            "000048": {"customer_id": "000048", "name": "آقای کمال باقری", "city": "بهشهر"},
            "000049": {"customer_id": "000049", "name": "آقای بابک مدنی", "city": "اراک"},
            "000050": {"customer_id": "000050", "name": "خانم نسا صالحی", "city": "ساوه"},
            "000051": {"customer_id": "000051", "name": "آقای یوسف سفاری", "city": "قشم"},
            "000052": {"customer_id": "000052", "name": "آقای مسعود سلیمی", "city": "هوم بندر عباس"},
            "000053": {"customer_id": "000053", "name": "آقای محمد قنبری", "city": "ملایر"},
            "000054": {"customer_id": "000054", "name": "آقای نادعلی نعیم ابادی", "city": "یزد"},
            "000055": {"customer_id": "000055", "name": "آقای ساسان کشاورز", "city": "بیضا"},
            "000056": {"customer_id": "000056", "name": "آقای مسعود همایون", "city": "مرو دشت"},
            "000057": {"customer_id": "000057", "name": "آقای حمید رمضانی", "city": "قزوین"},
            "000058": {"customer_id": "000058", "name": "آقای علی افسری", "city": "قم"},
            "000059": {"customer_id": "000059", "name": "آقای مسعود نوحی", "city": "کرمان"},
            "000060": {"customer_id": "000060", "name": "آقای محمد نژاد صالحی", "city": "سیرجان"},
            "000061": {"customer_id": "000061", "name": "آقای کیان", "city": "شهر بابک"},
            "000062": {"customer_id": "000062", "name": "آقای فرید سیاه بیدی", "city": "کرمانشاه"},
            "000063": {"customer_id": "000063", "name": "آقای ابوطالب حسینی", "city": "یاسوج"},
            "000064": {"customer_id": "000064", "name": "آقای میلاد پاکزاد", "city": "گچساران"},
            "000065": {"customer_id": "000065", "name": "آقای بهروز بحری", "city": "سقز"},
            "000066": {"customer_id": "000066", "name": "آقای یوسف بهرامیان", "city": "سنندج"},
            "000067": {"customer_id": "000067", "name": "آقای محسن عامریان", "city": "گنبد"},
            "000068": {"customer_id": "000068", "name": "آقای ابراهیم حسین زاده", "city": "گرگان"},
            "000069": {"customer_id": "000069", "name": "آقای کامران فلاح باقری", "city": "انزلی"},
            "000070": {"customer_id": "000070", "name": "آقای اروین محمدی", "city": "لاکانی رشت"},
            "000071": {"customer_id": "000071", "name": "آقای مصطفی کامران", "city": "رشت"},
            "000072": {"customer_id": "000072", "name": "آقای محمد دادرس", "city": "لاهیجان"},
            "000073": {"customer_id": "000073", "name": "آقای حسین بخشی", "city": "لنگرود"},
            "000074": {"customer_id": "000074", "name": "آقای علیرضا احمد خانی", "city": "تنکابن"},
            "000075": {"customer_id": "000075", "name": "آقای مهدی قلی زاده", "city": "هوم چالوس"},
            "000076": {"customer_id": "000076", "name": "آقای حسین مختاری", "city": "ساری"},
            "000077": {"customer_id": "000077", "name": "آقای مهدی خلدبرین", "city": "نور"},
            "000078": {"customer_id": "000078", "name": "آقای نیما کریمی", "city": ""},
            "000079": {"customer_id": "000079", "name": "آقای ابولفضل موسوی", "city": ""},
            "000080": {"customer_id": "000080", "name": "خانم مژده سلطان محمدی", "city": ""},
            "000081": {"customer_id": "000081", "name": "خانم احمدی", "city": ""},
            "000082": {"customer_id": "000082", "name": "آقای محمد طهماسبی", "city": ""},
            "000083": {"customer_id": "000083", "name": "آقای کمال محمدی", "city": ""},
            "000084": {"customer_id": "000084", "name": "خانم حمیرا عظیمی", "city": ""},
            "000085": {"customer_id": "000085", "name": "خانم سهیلا قمرپور", "city": ""},
            "000086": {"customer_id": "000086", "name": "آقای محمد رفیعی", "city": ""},
            "000087": {"customer_id": "000087", "name": "آقای سعیدپوررضایی", "city": "چالوس"},
            "000088": {"customer_id": "000088", "name": "آقای مسعود سلیمی", "city": "اپادانا بندر عباس"},
            "000089": {"customer_id": "000089", "name": "آقای مهدی کشاورز", "city": "هوم اهواز"},
            "000090": {"customer_id": "000090", "name": "آقای شاهرخ عاشوری", "city": "شیراز"},
            "000091": {"customer_id": "000091", "name": "آقای سعید حسنی", "city": "نصب"},
            "000092": {"customer_id": "000092", "name": "شرکت محترم اپادانا", "city": ""},
            "000093": {"customer_id": "000093", "name": "آقای میرعلی سید باقری", "city": ""},
            "000094": {"customer_id": "000094", "name": "خانم زهرامحمدی", "city": "اپادانا مارکت"},
            "000095": {"customer_id": "000095", "name": "آقای کشاورز", "city": "لاهیجان"},
            "000096": {"customer_id": "000096", "name": "آقای یعقوب عبداللهی", "city": "هوم"},
            "000097": {"customer_id": "000097", "name": "آقای رضا ترکمن", "city": "هوم کاسپین"},
            "000098": {"customer_id": "000098", "name": "آقای مرتضی انجیله ای", "city": "فروشگاه اینترنتی"},
            "000099": {"customer_id": "000099", "name": "آقای مجید ترابیان", "city": ""},
            "000100": {"customer_id": "000100", "name": "آقای سجاد بیضایی", "city": ""},
            "000101": {"customer_id": "000101", "name": "خانم جباری", "city": ""},
            "000102": {"customer_id": "000102", "name": "آقای مهدی مختاری", "city": "هوم ایرانمال"},
            "000103": {"customer_id": "000103", "name": "خانم پرویزی", "city": "شهریار"},
            "000104": {"customer_id": "000104", "name": "آقای پیام صالحی", "city": "آرتین مود"},
            "000105": {"customer_id": "000105", "name": "خانم مینو گلشن", "city": ""},
            "000106": {"customer_id": "000106", "name": "آقای مهدی مختاری", "city": "هوم ایرانمال"},
            "000107": {"customer_id": "000107", "name": "خانم پرویزی", "city": "شهریار"},
            "000108": {"customer_id": "000108", "name": "آقای پیام صالحی", "city": "آرتین مود"},
            "000114": {"customer_id": "000114", "name": "سلف بستنی باران", "city": ""},
            "000116": {"customer_id": "000116", "name": "هایپر حس نو", "city": ""}
        }
        
        logger.info(f"Customer database initialized with {len(self.customers)} customers")
    
    def authenticate_customer(self, customer_code: str) -> Optional[Dict[str, Any]]:
        """Authenticate customer by customer code"""
        # Clean the input code
        customer_code = customer_code.strip().replace(' ', '').replace('-', '')
        
        # Check if code is exactly 6 digits
        if not customer_code.isdigit() or len(customer_code) != 6:
            logger.warning(f"Invalid customer code format: {customer_code}")
            return None
        
        # Check if customer exists
        customer = self.customers.get(customer_code)
        
        if customer:
            logger.info(f"Customer authenticated successfully: {customer['name']} from {customer['city']}")
            return customer.copy()
        else:
            logger.warning(f"Customer code not found: {customer_code}")
            return None
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer information by ID"""
        return self.customers.get(customer_id)
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers (for admin use)"""
        return list(self.customers.values())
    
    def get_customers_by_city(self, city: str) -> List[Dict[str, Any]]:
        """Get all customers from a specific city"""
        return [customer for customer in self.customers.values() if customer['city'] == city]
    
    def get_customer_count(self) -> int:
        """Get total number of registered customers"""
        return len(self.customers)
    
    def get_cities(self) -> List[str]:
        """Get list of all cities"""
        cities = set(customer['city'] for customer in self.customers.values())
        return sorted(list(cities))
    
    def is_valid_customer_code(self, customer_code: str) -> bool:
        """Check if customer code format is valid"""
        if not customer_code:
            return False
        
        # Clean the input code
        customer_code = customer_code.strip().replace(' ', '').replace('-', '')
        
        # Check if code is exactly 6 digits
        return customer_code.isdigit() and len(customer_code) == 6
    
    def add_customer(self, customer_code: str, name: str, city: str) -> bool:
        """Add a new customer (admin function)"""
        if not self.is_valid_customer_code(customer_code):
            logger.error(f"Invalid customer code format: {customer_code}")
            return False
        
        if customer_code in self.customers:
            logger.warning(f"Customer code already exists: {customer_code}")
            return False
        
        self.customers[customer_code] = {
            'customer_id': customer_code,
            'name': name,
            'city': city
        }
        
        logger.info(f"New customer added: {name} from {city} with code {customer_code}")
        return True
    
    def update_customer(self, customer_code: str, name: str = None, city: str = None) -> bool:
        """Update customer information"""
        if customer_code not in self.customers:
            logger.error(f"Customer not found: {customer_code}")
            return False
        
        customer = self.customers[customer_code]
        
        if name:
            customer['name'] = name
        if city:
            customer['city'] = city
        
        logger.info(f"Customer updated: {customer_code}")
        return True
    
    def remove_customer(self, customer_code: str) -> bool:
        """Remove a customer (admin function)"""
        if customer_code not in self.customers:
            logger.error(f"Customer not found: {customer_code}")
            return False
        
        customer_name = self.customers[customer_code]['name']
        del self.customers[customer_code]
        
        logger.info(f"Customer removed: {customer_name} ({customer_code})")
        return True
