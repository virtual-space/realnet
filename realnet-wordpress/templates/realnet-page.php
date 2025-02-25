<?php
/**
 * Template for displaying Realnet pages
 */

get_header();

$content = $GLOBALS['realnet_content'] ?? array();
?>

<div id="primary" class="content-area">
    <main id="main" class="site-main">
        <article id="post-<?php echo esc_attr($content['id']); ?>" class="realnet-page">
            <header class="entry-header">
                <h1 class="entry-title"><?php echo esc_html($content['title']); ?></h1>
            </header>

            <div class="entry-content">
                <?php 
                    // Apply WordPress filters to content
                    echo apply_filters('the_content', $content['content']);
                ?>
            </div>

            <?php if (!empty($content['meta'])): ?>
            <footer class="entry-footer">
                <?php
                    // Add meta information
                    foreach ($content['meta'] as $key => $value) {
                        if (is_string($value)) {
                            printf(
                                '<span class="meta-%s">%s</span>',
                                esc_attr($key),
                                esc_html($value)
                            );
                        }
                    }
                ?>
            </footer>
            <?php endif; ?>
        </article>
    </main>
</div>

<?php
get_sidebar();
get_footer();
