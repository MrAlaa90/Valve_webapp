# Valve Management System

## Overview

This is a Django-based valve maintenance management system designed to track valves, spare parts, and maintenance history. The application provides both REST API endpoints and a web frontend for managing industrial valve maintenance operations. The system is configured to run on Replit with Arabic language support and RTL (right-to-left) layout.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Django 5.2.6** with Django REST Framework for API development
- **MVT (Model-View-Template) pattern** following Django conventions
- **Class-based views** for API endpoints using DRF generics
- **Function-based views** for frontend rendering

### Database Design
The system uses Django's ORM with the following core models:
- **Valve**: Primary entity with unique valve_id and optional drawing links
- **SparePart**: Catalog of available spare parts with unique part_id
- **PartCode**: Code system linking to spare parts
- **MaintenanceHistory**: Records of maintenance events with technician info, dates, and before/after images
- **MaintenancePart**: Junction table linking maintenance events to parts used

### API Architecture
- **RESTful API** design with standard CRUD operations
- **Serializers** for JSON data transformation
- **Generic API views** (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
- **URL routing** separated between API endpoints (/api/) and frontend views

### Frontend Architecture
- **Template inheritance** using Django's template system
- **Bootstrap 5.3.2** for responsive UI components
- **Arabic language support** with RTL layout
- **Static file handling** for CSS, JavaScript, and media files
- **Separate static directories** for CSS and JavaScript

### File Upload System
- **Image upload** functionality for maintenance before/after photos
- **Media file handling** with proper URL configuration
- **Static file serving** in development mode

### Security Configuration
- **CSRF protection** with trusted origins for Replit deployment
- **Secure cookie settings** for production readiness
- **Proxy SSL header** configuration for HTTPS handling
- **Debug mode** currently enabled for development

### Deployment Architecture
- **Replit-optimized** configuration with specific allowed hosts
- **ASGI/WSGI** support for different deployment scenarios
- **Static file collection** setup for production deployment

## External Dependencies

### Core Framework Dependencies
- **Django 5.2.6**: Web framework
- **Django REST Framework**: API development
- **Pillow**: Image processing for file uploads (implied by ImageField usage)

### Frontend Dependencies
- **Bootstrap 5.3.2**: CSS framework loaded via CDN
- **Bootstrap JavaScript**: Interactive components via CDN

### Deployment Platform
- **Replit**: Cloud development and hosting platform
- **Replit-specific configurations** for CSRF, SSL, and host settings

### Database
- **SQLite** (Django default): Development database
- **Migration system**: Database schema versioning

### Media and Static Files
- **Django static files**: CSS, JavaScript, and media handling
- **File upload system**: Image storage for maintenance records