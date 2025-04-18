// notifications.js
document.addEventListener('DOMContentLoaded', function() {
    const notificationList = document.getElementById('notification-list');
    const unreadCount = document.getElementById('unread-count');
    
    // Charge les notifications
    function loadNotifications() {
        fetch('/notifications/list/?json=1')
            .then(response => response.json())
            .then(data => {
                notificationList.innerHTML = '';
                
                if (data.notifications.length === 0) {
                    notificationList.innerHTML = '<div class="dropdown-item text-center">Aucune notification</div>';
                    return;
                }
                
                data.notifications.slice(0, 5).forEach(notification => {
                    const item = document.createElement('a');
                    item.href = notification.target_url;
                    item.className = 'dropdown-item';
                    if (notification.unread) {
                        item.className += ' fw-bold bg-light';
                    }
                    
                    const title = document.createElement('div');
                    title.className = 'd-flex justify-content-between';
                    
                    const verb = document.createElement('span');
                    verb.textContent = notification.verb;
                    
                    const time = document.createElement('small');
                    time.className = 'text-muted';
                    time.textContent = timeSince(new Date(notification.created_at));
                    
                    title.appendChild(verb);
                    title.appendChild(time);
                    
                    const description = document.createElement('div');
                    description.className = 'small';
                    description.textContent = notification.description;
                    
                    item.appendChild(title);
                    item.appendChild(description);
                    
                    notificationList.appendChild(item);
                });
            })
            .catch(error => {
                console.error('Erreur lors du chargement des notifications:', error);
                notificationList.innerHTML = '<div class="dropdown-item text-center">Erreur de chargement</div>';
            });
    }
    
    // Mise à jour du compteur de notifications
    function updateNotificationCount() {
        fetch('/notifications/unread-count/')
            .then(response => response.json())
            .then(data => {
                unreadCount.textContent = data.count;
                if (data.count > 0) {
                    unreadCount.classList.remove('d-none');
                } else {
                    unreadCount.classList.add('d-none');
                }
            });
    }
    
    // Rafraîchissement périodique
    setInterval(() => {
        updateNotificationCount();
    }, 30000); // Toutes les 30 secondes
    
    // Marquer toutes les notifications comme lues
    document.querySelectorAll('.mark-all-read').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            fetch('/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateNotificationCount();
                    loadNotifications();
                }
            });
        });
    });
    
    // Charge les notifications au chargement
    if (notificationList) {
        loadNotifications();
        
        // Événement d'ouverture du dropdown
        document.getElementById('navbarDropdownNotifications').addEventListener('click', function() {
            loadNotifications();
        });
    }
    
    // Utilitaire pour formater le temps écoulé
    function timeSince(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        let interval = seconds / 31536000;
        if (interval > 1) return Math.floor(interval) + " an(s)";
        
        interval = seconds / 2592000;
        if (interval > 1) return Math.floor(interval) + " mois";
        
        interval = seconds / 86400;
        if (interval > 1) return Math.floor(interval) + " jour(s)";
        
        interval = seconds / 3600;
        if (interval > 1) return Math.floor(interval) + " heure(s)";
        
        interval = seconds / 60;
        if (interval > 1) return Math.floor(interval) + " minute(s)";
        
        return Math.floor(seconds) + " seconde(s)";
    }
    
    // Utilitaire pour récupérer un cookie
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});