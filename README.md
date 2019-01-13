hovr
===============
Home network video recorder (based on VideoLAN)

# Run

```
sudo docker-compose up -d
sudo docker exec -it hovr_hovr_1 "python manage.py createsuperuser"
```

# API
- `/api/inventory` - inventory
- `/api/recorder` - recorder
- `/admin` - django administration