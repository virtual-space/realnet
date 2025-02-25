<?php
/**
 * Template for displaying Realnet posts
 */

get_header();

$content = $GLOBALS['realnet_content'] ?? array();
?>

<div id="primary" class="content-area">
    <main id="main" class="site-main">
        <article id="post-<?php echo esc_attr($content['id']); ?>" class="realnet-post">
            <header class="entry-header">
                <h1 class="entry-title"><?php echo esc_html($content['title']); ?></h1>

                <div class="entry-meta">
                    <?php if (!empty($content['author'])): ?>
                    <span class="author">
                        <?php echo esc_html($content['author']); ?>
                    </span>
                    <?php endif; ?>

                    <?php if (!empty($content['date'])): ?>
                    <span class="posted-on">
                        <?php echo esc_html(date('F j, Y', strtotime($content['date']))); ?>
                    </span>
                    <?php endif; ?>

                    <?php if (!empty($content['categories'])): ?>
                    <span class="categories">
                        <?php echo esc_html(implode(', ', $content['categories'])); ?>
                    </span>
                    <?php endif; ?>
                </div>
            </header>

            <?php if (!empty($content['excerpt'])): ?>
            <div class="entry-excerpt">
                <?php echo esc_html($content['excerpt']); ?>
            </div>
            <?php endif; ?>

            <div class="entry-content">
                <?php 
                    // Apply WordPress filters to content
                    echo apply_filters('the_content', $content['content']);
                ?>
            </div>

            <footer class="entry-footer">
                <?php if (!empty($content['tags'])): ?>
                <div class="tags-links">
                    <?php echo esc_html(implode(', ', $content['tags'])); ?>
                </div>
                <?php endif; ?>

                <?php if (!empty($content['meta'])): ?>
                <div class="entry-meta">
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
                </div>
                <?php endif; ?>

                <?php
                    // Add social sharing buttons if theme supports it
                    if (function_exists('the_social_sharing_buttons')) {
                        the_social_sharing_buttons();
                    }
                ?>
            </footer>

            <?php
                // Add comments if theme supports it
                if (comments_open() || get_comments_number()) {
                    comments_template();
                }
            ?>
        </article>

        <?php
            // Add post navigation if theme supports it
            the_post_navigation(array(
                'prev_text' => __('Previous Post'),
                'next_text' => __('Next Post'),
            ));
        ?>
    </main>
</div>

<?php
get_sidebar();
get_footer();
