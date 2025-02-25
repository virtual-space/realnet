#!/bin/bash
set -e

# Function to log messages with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for database
log "Waiting for database connection..."
until mysqladmin ping -h"$WORDPRESS_DB_HOST" -u"$WORDPRESS_DB_USER" -p"$WORDPRESS_DB_PASSWORD" --silent; do
  log "Database not ready, retrying..."
  sleep 5
done
log "Database connection established"

# Switch to www-data user for all WordPress operations
cd /var/www/html

# Configure wp-cli
log "Configuring wp-cli..."
mkdir -p /var/www/.wp-cli
cat > /var/www/.wp-cli/config.yml << 'WPCONFIG'
apache_modules:
  - mod_rewrite
path: /var/www/html
url: http://localhost:8081
user: admin
WPCONFIG
chown -R www-data:www-data /var/www/.wp-cli

# Function to run wp-cli as www-data
wp_run() {
  runuser -u www-data -- wp "$@" --allow-root
}

# Wait for WordPress
log "Waiting for WordPress installation..."
until wp_run core is-installed; do
  log "WordPress not ready, retrying..."
  sleep 5
done
log "WordPress installation detected"

# Setup multisite
if ! wp_run core is-installed --network 2>/dev/null; then
  log "Setting up multisite..."
  wp_run core multisite-convert --title="Realnet WordPress" --base="/"
  
  # Update .htaccess for multisite
  log "Configuring multisite rewrite rules..."
  wp_run rewrite structure '/%postname%/'
  wp_run rewrite flush --hard
  
  # Create main site pages
  log "Creating main site pages..."
  wp_run post create --post_type=page --post_title='Home' --post_status=publish
  wp_run post create --post_type=page --post_title='About' --post_status=publish
  wp_run option update show_on_front 'page'
  wp_run option update page_on_front $(wp_run post list --post_type=page --post_status=publish --posts_per_page=1 --pagename=home --format=ids)
  
  log "Multisite setup complete"
fi

# Install and activate plugins
log "Installing and activating plugins..."
wp_run plugin install jwt-authentication-for-wp-rest-api --activate
wp_run plugin install advanced-custom-fields --activate
wp_run plugin install wp-rest-api-v2-menus --activate
wp_run plugin install members --activate

# Install realnet plugin
log "Installing realnet plugin..."
mkdir -p /var/www/html/wp-content/plugins/realnet
cp -r /docker-entrypoint-initwp.d/realnet/* /var/www/html/wp-content/plugins/realnet/
chown -R www-data:www-data /var/www/html/wp-content/plugins/realnet
wp_run plugin activate realnet

# Setup admin user
if ! wp_run user get admin 2>/dev/null; then
  log "Creating admin user..."
      wp_run user create "$WORDPRESS_ADMIN_USER" admin@realnet.local --role=administrator --user_pass="$WORDPRESS_ADMIN_PASSWORD" --display_name="Administrator" --first_name="Admin" --last_name="User"
  log "Admin user created"
fi

# Grant super admin privileges and configure main site
log "Configuring admin privileges and site settings..."
    wp_run super-admin add "$WORDPRESS_ADMIN_USER"
wp_run option update blogname "Realnet WordPress"
wp_run option update blogdescription "Realnet WordPress Multisite"
wp_run option update admin_email "admin@realnet.local"

# Enable pretty permalinks
log "Configuring permalinks..."
wp_run rewrite structure '/%postname%/'
wp_run rewrite flush --hard

log "WordPress setup complete"
