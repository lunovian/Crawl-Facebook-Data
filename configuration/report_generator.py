import pandas as pd
import os
from datetime import datetime
import json

class ReportGenerator:
    def __init__(self, base_data_dir="data"):
        self.base_data_dir = base_data_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def analyze_page_data(self, page_name):
        """Analyze data completeness for a page"""
        page_dir = os.path.join(self.base_data_dir, page_name)
        if not os.path.exists(page_dir):
            return []

        posts_data = []
        for post_id in os.listdir(page_dir):
            post_dir = os.path.join(page_dir, post_id)
            if not os.path.isdir(post_dir):
                continue

            post_data = {
                'page_name': page_name,
                'post_id': post_id,
                'has_caption': os.path.exists(os.path.join(post_dir, 'caption.txt')),
                'has_comments': os.path.exists(os.path.join(post_dir, 'comments.txt')),
                'media_count': len([f for f in os.listdir(post_dir) if f.endswith(('.jpg', '.mp4'))]),
                'timestamp': datetime.fromtimestamp(os.path.getctime(post_dir)).strftime("%Y-%m-%d %H:%M:%S")
            }

            # Check content of files
            if post_data['has_caption']:
                with open(os.path.join(post_dir, 'caption.txt'), 'r', encoding='utf-8') as f:
                    post_data['caption_length'] = len(f.read().strip())
            else:
                post_data['caption_length'] = 0

            if post_data['has_comments']:
                with open(os.path.join(post_dir, 'comments.txt'), 'r', encoding='utf-8') as f:
                    post_data['comment_count'] = len(f.readlines())
            else:
                post_data['comment_count'] = 0

            posts_data.append(post_data)

        return posts_data

    def generate_reports(self):
        """Generate comprehensive reports"""
        all_data = []
        summary_data = []

        # Analyze all pages
        for page_name in os.listdir(self.base_data_dir):
            if os.path.isdir(os.path.join(self.base_data_dir, page_name)):
                page_data = self.analyze_page_data(page_name)
                all_data.extend(page_data)
                
                # Generate page summary
                if page_data:
                    summary = {
                        'page_name': page_name,
                        'total_posts': len(page_data),
                        'posts_with_caption': sum(1 for p in page_data if p['has_caption']),
                        'posts_with_comments': sum(1 for p in page_data if p['has_comments']),
                        'total_comments': sum(p['comment_count'] for p in page_data),
                        'total_media': sum(p['media_count'] for p in page_data),
                        'missing_content': sum(1 for p in page_data if not (p['has_caption'] and p['has_comments'] and p['media_count'] > 0))
                    }
                    summary_data.append(summary)

        # Create DataFrames
        df_detailed = pd.DataFrame(all_data)
        df_summary = pd.DataFrame(summary_data)

        # Save reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as Excel with multiple sheets
        excel_path = os.path.join(self.reports_dir, f'facebook_crawler_report_{timestamp}.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            df_detailed.to_excel(writer, sheet_name='Detailed', index=False)

        # Save as CSVs
        df_summary.to_csv(os.path.join(self.reports_dir, f'summary_report_{timestamp}.csv'), index=False)
        df_detailed.to_csv(os.path.join(self.reports_dir, f'detailed_report_{timestamp}.csv'), index=False)

        return excel_path
