# Persian E-commerce Telegram Bot

## Overview

This is a comprehensive Persian e-commerce Telegram bot designed for selling bedding and home textile products. The bot provides a complete shopping experience with customer authentication, hierarchical product browsing, shopping cart management, and invoice generation. The system is built using the python-telegram-bot library and follows a modular architecture with clear separation of concerns.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Bot Layer**: Handles Telegram API interactions using the python-telegram-bot library with handlers for commands, callbacks, and messages
- **Data Layer**: Manages customer database and product catalog using static data structures stored in Python dictionaries
- **Business Logic Layer**: Processes cart operations, pricing calculations, discount management, and invoice generation
- **Utilities Layer**: Provides logging, Persian language support, text formatting, and number conversion utilities

The architecture is designed for maintainability and scalability, with each module having specific responsibilities. The system uses JSON file-based persistence for cart data and maintains user session state in memory.

## Key Components

### 1. Bot Management (`bot/`)
- **handlers.py**: Main bot handlers for commands (/start, /help), callback queries, and message processing with session management
- **keyboards.py**: All inline keyboard layouts including main menu, category selection, alphabetical search navigation, and product selection interfaces
- **cart.py**: Shopping cart management with JSON file-based persistence in `cart_data/` directory, supporting add/remove/clear operations
- **pricing.py**: Product pricing engine with fixed category prices, discount calculations (30% cash, 25% installment), 9% tax computation, and invoice generation
- **config.py**: Configuration management using environment variables (BOT_TOKEN, ADMIN_IDS, LOG_LEVEL, CART_DATA_DIR, MAX_CART_ITEMS)

### 2. Data Management (`data/`)
- **product_data.py**: Complete product catalog with 6 main categories and fixed pricing:
  - Baby bedding: 4,780,000 toman (19+ products)
  - Teen bedding: 4,780,000 toman
  - Adult bedding: 5,600,000 toman
  - Curtains: 3,500,000 toman
  - Cushions: 2,800,000 toman
  - Tablecloth & runners: 2,200,000 toman
- **customer_service.py**: Customer database with 30+ registered customers, each with unique 6-digit authentication codes, names, and cities

### 3. Utilities (`utils/`)
- **logger.py**: Centralized logging system with console output, configurable log levels, and timestamp formatting
- **persian_utils.py**: Persian language utilities including bidirectional number conversion (Persian ↔ English digits), price formatting with thousand separators, and text processing functions

## Recent Changes (August 11, 2025)

### Migration and Bug Fixes Completed
- **Environment Migration**: Successfully completed migration from Replit Agent to standard Replit environment
- **Dependencies Verified**: All required packages (python-telegram-bot==20.7, requests, schedule) properly installed
- **Bot Functionality**: Bot server running successfully with all handlers and schedulers active
- **Database Integration**: Customer database initialized with 110 customers
- **Size Selection Error Fixed**: Added error handling and session management improvements for size selection process
- **Payment Flow Enhancement**: Standardized both 60-day and 90-day payment flows to show invoice with amounts → cash/check selection → process accordingly
- **Payment System Standardization**: Both 60-day and 90-day payments now follow consistent two-stage flow with proper callback data routing
- **Check Payment System Fixed**: Complete check payment workflow restored and fixed for all payment methods (cash, 60-day, 90-day)
- **Admin Recipient System**: Admins can assign checks to specific recipients (فرانک غریبی, نیما کریمی, مجید ترابیان, وحید ترابیان) with national ID information
- **Customer Confirmation Flow**: After admin assigns recipient, customer receives national ID info and confirms 10-day delivery commitment
- **Final Order Management**: When customer confirms 10-day delivery, final invoice with simplified management buttons (تایید سفارش, در حال پیگیری, سفارش ارسال شد) sent to support group only
- **Payment Info Compatibility**: Fixed compatibility between check_payment_info and payment_info for 60/90-day check payments

### Enhanced Two-Stage Payment System Completed
- **Payment Method Selection**: First stage now shows 60/90 day payment options with discount calculations
- **Payment Type Selection**: Second stage offers Cash vs Check payment types for each method
- **Check Payment Workflow**: Complete check payment system with photo upload functionality
- **Admin Verification System**: Support group receives check photos with admin action buttons
- **Customer Communication Flow**: Automated messaging system for check processing status updates
- **Persian Instructions**: Check payment includes specific Persian delivery instructions (10-day requirement)

### Check Payment Features (August 11, 2025)
- **Photo Upload System**: Customers can upload check photos directly in bot
- **Admin Processing**: Support group gets check photos with verification buttons
- **Status Tracking**: Customers can track check processing status via "در حال پیگیری" button
- **Delivery Requirements**: Clear 10-day delivery instruction to factory accounting
- **Complete Integration**: Check orders fully integrated with existing order management system

### Enhanced Check Payment System (August 11, 2025)
- **Specific Admin Recipients**: Replaced generic admin buttons with specific recipient buttons:
  - خانم فرانک غریبی (National ID: 0012311138)
  - نیما کریمی (National ID: 0451640594) 
  - مجید ترابیان (National ID: 007335310)
  - وحید ترابیان (National ID: 0077860357)
- **Customer Confirmation System**: Added "چک را ثبت کرده ام وتا 10 روز کاری ارسال خواهم کرد" button in customer chat only
- **Clean Admin Interface**: Admin support group shows only recipient selection buttons, no customer actions
- **Automatic Re-submission**: Customer confirmation resends invoice and check photo to support group
- **Personalized Messages**: Each recipient selection sends specific message with name and national ID
- **Complete Integration**: All features work seamlessly with existing payment system

### Bug Fixes and Maintenance (August 11, 2025)
- **Fixed Category Navigation**: Resolved issue where clicking product categories showed default message
- **Fixed Photo Upload Error**: Resolved KeyError when payment_info is missing during check photo upload
- **Added Missing Methods**: Added public `generate_order_id()` and `save_order()` methods to OrderManagementServer
- **Enhanced Error Logging**: Improved callback error reporting for better debugging
- **Removed Check Confirmation Message**: Removed "✅ عکس چک دریافت شد و برای تیم پشتیبانی ارسال شد" message for cleaner user experience
- **Clean Interface Updates**: Removed customer confirmation button from admin support group keyboards
- **Preserved Existing Functionality**: All original bot features remain intact and functional

## Previous Changes (August 10, 2025)

### Migration Completed
- **Replit Environment Migration**: Successfully migrated from Replit Agent to standard Replit environment
- **Dependencies Updated**: Installed python-telegram-bot==20.7 and requests packages via package manager
- **Security Enhancement**: Configured BOT_TOKEN as environment variable for secure token management
- **Bot Activation**: DecoTeen Telegram Bot is now running successfully with proper configuration

### Hesabfa Integration Status
- **Integration Attempted**: Attempted comprehensive integration with Hesabfa accounting system
- **Network Limitation Confirmed**: Replit environment cannot access Hesabfa API endpoints due to network restrictions
- **Alternative Implementation**: Complete order data logging system implemented for manual invoice creation workflow
- **Order Management**: Enhanced order tracking and status management with detailed logging for admin workflow

### UI Improvements Completed (August 10, 2025)
- **Pagination System**: Added pagination buttons ("دکمه صفحه بعد") for all product categories
- **Button Layout**: Improved column alignment with 8 items per page (4 rows × 2 buttons) for better navigation
- **Categories Enhanced**: Baby, Curtain, Cushion, Tablecloth, and alphabetical search now support pagination
- **Navigation Flow**: Updated handlers to support pagination navigation with proper state management

### Enhanced Order Cancellation System (August 10, 2025)
- **Remaining Balance Display**: When admin cancels an order, customer sees detailed invoice breakdown with remaining balance amount
- **Payment Recovery Flow**: Added "واریز مانده حساب" button for cancelled orders to allow balance payment
- **Receipt Processing**: Customers can upload receipt photos for remaining balance payments
- **Admin Re-approval**: System sends receipt to support group with admin buttons for order re-confirmation
- **Streamlined Interface**: Cancelled orders show only "Contact Support" and "Pay Remaining Balance" buttons
- **Complete Workflow**: Full cycle from cancellation → balance payment → receipt upload → admin approval → order reactivation

## Previous Changes (July 27, 2025)

- **Direct Catalog Access**: After authentication, customers now see the product catalog immediately instead of welcome page
- **Updated Product Data**: Baby products now include authentic names like "فارست" and "بو" from original catalog
- **Size Restrictions**: 
  - Baby category: Only 70×160 size available
  - Teen/Adult categories: Removed 75×160 size option
- **Enhanced Payment Options**: Added 90-day payment option (25% discount + 25% advance payment)
- **Improved Invoice**: Includes discount calculations and detailed payment breakdown

## Data Flow

1. **User Authentication**: Customer enters unique 6-digit code → system validates against customer database → authenticated session created → direct catalog display
2. **Product Browsing**: Category selection → subcategory (for curtains) → alphabetical search using Persian keyboard → product selection with category-specific size options
3. **Cart Management**: Add products with size/quantity selection → view cart with itemized breakdown → modify quantities or remove items
4. **Checkout Process**: Generate invoice with customer details → calculate discounts and taxes → display three payment options (cash 30%, installment 25%, 90-day 25% + 25% advance)

## External Dependencies

- **python-telegram-bot**: Core Telegram Bot API wrapper for handling updates, commands, and callbacks
- **Python Standard Library**: json for cart persistence, os for file operations, logging for system monitoring, datetime for invoice timestamps
- **No database dependencies**: Uses file-based JSON storage for cart data and in-memory dictionaries for product/customer data

## Deployment Strategy

The application is configured for deployment on Replit with:

- **Environment Variables**: BOT_TOKEN (required), ADMIN_IDS, LOG_LEVEL, CART_DATA_DIR, MAX_CART_ITEMS
- **File Structure**: Modular package structure with clear separation between bot logic, data management, and utilities
- **Persistence**: JSON files in `cart_data/` directory for shopping cart storage
- **Error Handling**: Comprehensive logging and graceful error recovery throughout the application
- **Session Management**: In-memory user session tracking for authentication state and navigation context

The bot is designed to be stateless regarding user authentication (relies on customer code validation) but maintains cart state through file persistence, making it suitable for cloud deployment environments.