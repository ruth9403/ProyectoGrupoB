# ProyectoBlogGrupoB

Proyecto final Mision Tic Universidad del Norte, Grupo B


## CONFIGURAR SERVIDOR FLASK
Ver [Enlace de ayuda](https://medium.com/faun/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a)

## DESPLIEGUE

### Conectarse con el servidor:
Conectarse en Powershell/bash/cualquiera:
```console
ssh -i "miPrimerAWS.pem" ubuntu@ec2-54-81-132-139.compute-1.amazonaws.com
```

### Actualizar repo
hacer commit de los cambios al repositorio
```console
cd /home/ubuntu/ProyectoBlogGrupoB

git push
```

### Actualizar app.service
```console
sudo cp app.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl restart app
```

### Editar nginx 
En caso de ser necesario
```console
sudo nano /etc/nginx/sites-available/app

sudo systemctl restart nginx

```

### Actualizar aplicación
Ver [Enlace de ayuda](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units)

```console
sudo systemctl restart app

sudo systemctl status app
```

## MANTENIMIENTO - REVISION
### Revisar logs de aplicación
Ver [Enlace de ayuda](https://www.digitalocean.com/community/tutorials/how-to-use-journalctl-to-view-and-manipulate-systemd-logs)
```console
sudo journalctl -u app
```
## INTEGRANTES:
Ver [Enlace de ayuda](https://remarkablemark.org/blog/2019/10/17/github-contributors-readme/)
- María Isabel Jaramillo @fandemisterling100
- 
