import requests
from bs4 import BeautifulSoup
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from fpdf import FPDF
from datetime import datetime
from collections import Counter

class PDF(FPDF):
    
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'SEO Analysis Report', 0, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(8)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 12)
        if isinstance(body, list):
            for line in body:
                self.multi_cell(0, 10, line, align='L')
                self.ln(5)  # Zusätzlicher Zeilenabstand zwischen den Zeilen
        else:
            self.multi_cell(0, 10, body, align='L')
            self.ln(5)  # Zusätzlicher Zeilenabstand nach dem Text
        self.ln()

    def add_chapter(self, title, content):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(content)

    def add_tfidf_table(self, top_words):
        self.set_font('Helvetica', 'B', 12)
        col_width = self.w / 4.5
        row_height = self.font_size + 2
        for word, score in top_words:
            self.cell(col_width, row_height, word, border=1)
            self.cell(col_width, row_height, f'{score:.2%}', border=1, ln=True)
            
    def cover_page(self):
        self.add_page()
        self.set_font('Helvetica', 'B', 24)
        self.cell(0, 60, 'SEO Analysis Report', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 12)
        self.cell(0, 10, 'Generated on ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1, 'C')

def fetch_page(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def analyze_meta_tags(soup):
    results = ""
    title = soup.title.string if soup.title else 'No title found'
    results += f'Title: {title}\n'

    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description_content = meta_description['content'] if meta_description else 'No meta description found'
    results += f'Meta Description: {meta_description_content}\n'

    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    meta_keywords_content = meta_keywords['content'] if meta_keywords else 'No meta keywords found'
    results += f'Meta Keywords: {meta_keywords_content}\n'
    return results

def analyze_headings(soup):
    results = ""
    for i in range(1, 7):
        headers = soup.find_all(f'h{i}')
        for header in headers:
            results += f'H{i}: {header.get_text(strip=True)}\n'
    return results

def analyze_images(soup):
    results = ""
    images = soup.find_all('img')
    for img in images:
        alt_text = img.get('alt')
        src = img.get('src')
        results += f'Image: {src}, Alt Text: {alt_text if alt_text else "No alt text"}\n'
    return results

def analyze_links(soup):
    results = ""
    internal_links = []
    external_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http://localhost') or href.startswith('/'):
            internal_links.append(href)
        else:
            external_links.append(href)

    results += f'Internal Links: {internal_links}\n'
    results += f'External Links: {external_links}\n'
    return results

def analyze_load_time(url):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()

    load_time = end_time - start_time
    return f'Page Load Time: {load_time} seconds\n'

def analyze_tfidf(soup):
    text_content = soup.get_text()
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text_content])

    feature_names = vectorizer.get_feature_names_out()
    dense = tfidf_matrix.todense().tolist()[0]

    word_scores = [(feature_names[i], dense[i]) for i in range(len(feature_names))]
    word_scores.sort(key=lambda x: x[1], reverse=True)

    return word_scores[:10]

def analyze_structured_data(soup):
    results = ""
    structured_data = soup.find_all('script', attrs={'type': 'application/ld+json'})
    for data in structured_data:
        results += f'Structured Data: {data.get_text(strip=True)}\n'
    return results

def analyze_viewport(soup):
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    viewport_content = viewport['content'] if viewport else 'No viewport meta tag found'
    return f'Viewport: {viewport_content}\n'

def main():
    url = input("Bitte geben Sie die URL der Seite ein, die Sie analysieren möchten: ")
    soup = fetch_page(url)

    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    meta_tags_analysis = analyze_meta_tags(soup)
    headings_analysis = analyze_headings(soup)
    images_analysis = analyze_images(soup)
    links_analysis = analyze_links(soup)
    load_time_analysis = analyze_load_time(url)
    tfidf_analysis = analyze_tfidf(soup)
    structured_data_analysis = analyze_structured_data(soup)
    viewport_analysis = analyze_viewport(soup)

    print(meta_tags_analysis)
    print(headings_analysis)
    print(images_analysis)
    print(links_analysis)
    print(load_time_analysis)
    print(tfidf_analysis)
    print(structured_data_analysis)
    print(viewport_analysis)

    pdf.add_chapter("Meta Tags Analysis", meta_tags_analysis)
    pdf.add_chapter("Headings Analysis", headings_analysis)
    pdf.add_chapter("Images Analysis", images_analysis)
    pdf.add_chapter("Links Analysis", links_analysis)
    pdf.add_chapter("Load Time Analysis", load_time_analysis)
    pdf.add_chapter("TF-IDF Analysis", [f'{word}: {score:.2%}' for word, score in tfidf_analysis])
    pdf.add_chapter("Structured Data Analysis", structured_data_analysis)
    pdf.add_chapter("Viewport Analysis", viewport_analysis)
    
    pdf.add_page()
    pdf.chapter_title("Top 10 Most Used Words (TF-IDF)")
    pdf.add_tfidf_table(tfidf_analysis)

    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf.output(f'report_{current_datetime}.pdf')
    
if __name__ == '__main__':
    main()
