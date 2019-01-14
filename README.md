hovr
===============
Home network video recorder for IP camera (based on VideoLAN)

Used with my Hikvision IP cameras that supports RTP H.264 streaming. 
The main goals is:
1. capture a streams and write short pieces in organized path structure
2. take periodic snapshots
3. recycle obsoleted recordings
4. provide REST API
5. user friendly configurations for camera, schedule and recording profiles

License: GPLv3

Contributors
- Denis Muratov <xeronm@gmail.com>

# Run docker compose

Edit `.env` file and setup parameters like `port` and `data_path`

```
sudo docker-compose up -d
sudo docker exec -it hovr_hovr_1 python manage.py createsuperuser
```

# API
- `/api/inventory` - inventory
- `/api/recorder` - recorder
- `/admin` - django administration