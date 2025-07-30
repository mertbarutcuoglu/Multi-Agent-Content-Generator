import os
import uuid
import io
import logging
from selenium import webdriver
from PIL import Image, ImageDraw
from jinja2 import Environment
from markdown import markdown
from markupsafe import Markup
from base64 import b64encode


# ImageGenerator is a class responsible for generating images from HTML templates using Jinja2 and Selenium.
class ImageGenerator:
    def __init__(self):
        self.env = self.build_jinja_env()
        self.driver = webdriver.Firefox()
        self.out_dir = os.path.join(os.path.dirname(__file__), "out")
        os.makedirs(self.out_dir, exist_ok=True)

    def get_output_path(self, filename: str) -> str:
        return os.path.join(self.out_dir, filename)

    def build_jinja_env(self) -> Environment:
        """
        Builds and returns a Jinja2 environment with custom filters for markdown processing and image encoding.
        """

        def safe_markdown(text: str) -> Markup:
            return Markup(markdown(text, extensions=["smarty"]))

        def strip_markdown(text: str) -> str:
            """
            Removes the <p> and </p> tags added by default.
            """
            return safe_markdown(text)[3:-4]

        def img_encode(img_path: str) -> str:
            """
            Checks if a provided image is a local image or a remote image.
            If local, encodes the image as a base64 string,
            required for local images to display in the Chromedriver.
            """
            if not img_path:
                return ""

            if os.path.isfile(img_path):
                with open(img_path, "rb") as f:
                    img_str = str(b64encode(f.read()))[2:-1]
                img_type = img_path[-3:]
                img_str = f"data:image/{img_type};base64,{img_str}"
            else:
                logging.info(f"Downloading {img_path}")
                img_str = img_path

            return img_str

        env = Environment()
        env.filters.update(
            {
                "markdown": strip_markdown,
                "markdown_nostrip": safe_markdown,
                "img_encode": img_encode,
            }
        )
        return env

    def generate_html_from_template(self, template: str, data: dict) -> str:
        """
        Generates an HTML file from a given template and data dictionary, writes the output to a file,
        and returns the file path.
        """
        with open(template, "r", encoding="utf-8") as f:
            template = self.env.from_string(f.read())

        output = template.render(data)
        output_file = self.get_output_path("rendered_html.html")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(output)

        logging.info(f"HTML file generated: {output_file}")
        return output_file

    def get_template_path(self, template: str) -> str:
        """
        Resolves and returns the full path to a template file. Raises FileNotFoundError if the template is not found.
        """
        if os.path.exists(template):
            return template

        dirname = os.path.dirname(__file__)
        template = os.path.join(dirname, "assets", template)

        if not os.path.exists(template):
            raise FileNotFoundError(f"Template '{template}' not found")

        return template

    def generate_reddit_title_image(
        self, title: str, author: str, subreddit: str
    ) -> str:
        """
        Generates an image for a Reddit post title using a template, renders it in a browser,
        captures a screenshot, and saves the image with rounded corners. Returns the file path of the saved image.
        """
        template_path = self.get_template_path("reddit.html")
        html_path = self.generate_html_from_template(
            template_path, {"title": title, "author": author, "subreddit": subreddit}
        )

        self.driver.maximize_window()
        self.driver.get("file://" + os.path.abspath(html_path))

        element = self.driver.find_element(by="class name", value="reddit-box")
        fname = self.get_output_path(f"{uuid.uuid4()}.png")

        img = Image.open(io.BytesIO(element.screenshot_as_png))
        img = img.resize((int(img.width * 0.85), int(img.height * 0.85)))
        img = self.add_corners(img, 25)

        img.save(fname)
        self.quit_image_generator()

        return fname

    def add_corners(self, im: Image.Image, rad: int) -> Image.Image:
        """
        Adds rounded corners to an image and returns the modified image.
        """
        circle = Image.new("L", (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
        alpha = Image.new("L", im.size, 255)

        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))

        im.putalpha(alpha)
        self.driver.close()
        return im

    def quit_image_generator(self):
        """
        Closes and quits the Selenium WebDriver.
        """
        self.driver.quit()
