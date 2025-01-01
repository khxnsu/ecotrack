# EcoTrack

A professional sustainability tracking platform built with Django that helps organizations monitor and manage their environmental impact. Available in both Community and Commercial editions.

## Editions

### Community Edition (Open Source)
- Core sustainability tracking features
- Basic user management
- Standard reporting
- Community support
- AGPL v3 licensed

### Commercial Edition
- All Community Edition features
- Advanced analytics and reporting
- Enterprise user management
- White-label options
- Custom integrations
- Priority support
- Service Level Agreements
- Commercial license

## Features

### Core Features (Community Edition)
- **User Management**
  - Basic authentication and authorization
  - Personal dashboard
  - Profile management

- **Eco Activities**
  - Activity tracking
  - Basic impact assessment
  - Location tracking
  - Category management
  - Verification system

- **Sustainability Goals**
  - Goal setting and tracking
  - Progress visualization
  - Deadline management
  - Basic reminder system
  - Status tracking

- **Admin Interface**
  - Standard Django admin customization
  - Progress tracking
  - Basic filtering
  - Activity verification

### Premium Features (Commercial Edition)
- **Advanced Analytics**
  - Custom reporting
  - Data export
  - Trend analysis
  - Predictive insights

- **Enterprise Management**
  - Role-based access control
  - Team management
  - Multi-site support
  - Custom workflows

- **Integration & API**
  - REST API access
  - Custom integrations
  - Third-party system connectivity
  - Automated data import/export

- **Premium Support**
  - Dedicated support team
  - Priority bug fixes
  - Feature request priority
  - Implementation assistance

## Technical Details

### Models
- **EcoActivity**
  - Environmental action tracking
  - Impact assessment
  - Geolocation support
  - Temporal tracking

- **SustainabilityGoal**
  - Progress calculation
  - Deadline management
  - Priority system
  - Reminder functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/khxnsu/ecotrack.git
```

2. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Make sure to update:
# - DJANGO_SECRET_KEY
# - DEBUG
# - ALLOWED_HOSTS
# - EMAIL settings (if using email features)
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Deployment

This project is configured for deployment on Render. To deploy:

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn ecotrack.wsgi:application`
   - Python Version: 3.9
   - Environment Variables:
     - `DJANGO_SECRET_KEY`: Your secret key
     - `DJANGO_DEBUG`: False
     - `ALLOWED_HOSTS`: Your Render domain

## Usage

1. Access the admin interface at `/admin`
2. Create and manage eco activities and sustainability goals
3. Track progress through the dashboard
4. Monitor and verify activities
5. Set and manage environmental goals

## Contributing

We welcome contributions to the Community Edition of EcoTrack:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please note that all contributions to the Community Edition will be licensed under AGPL v3.

## Licensing

EcoTrack is available under a dual-license model:

1. **Community Edition**: GNU Affero General Public License v3.0 (AGPL v3)
   - Free to use, modify, and distribute
   - Modifications must be shared with the community
   - Source code must be made available

2. **Commercial Edition**: Proprietary License
   - Includes premium features
   - Enterprise support
   - Custom development options
   - No open source requirements

For commercial licensing inquiries, please contact adrianparedezdev@gmail.com.

## Support

- Community Edition: GitHub Issues
- Commercial Edition: Contact adrianparedezdev@gmail.com
