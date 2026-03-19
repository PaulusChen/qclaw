"""
TEST-E2E-001: 端到端流程测试 (更新版)
包含新增的 DeepLearning 页面测试
"""
import pytest
from playwright.sync_api import Page, expect
import re


class TestHomepageFlow:
    """首页流程测试"""
    
    def test_homepage_loads_successfully(self, page: Page):
        """测试首页加载成功"""
        page.goto("http://localhost:80")
        expect(page).to_have_title(re.compile("QCLaw|Dashboard", re.IGNORECASE))
        expect(page.locator("body")).to_be_visible()
    
    def test_homepage_shows_market_indices(self, page: Page):
        """测试首页显示大盘指标"""
        page.goto("http://localhost:80")
        # 检查是否有大盘指标相关元素
        expect(page.locator(".market-indices, .market-card, .index")).to_be_visible(timeout=10000)
    
    def test_navigation_to_deep_learning(self, page: Page):
        """测试导航到深度学习页面"""
        page.goto("http://localhost:80")
        # 查找深度学习导航链接
        dl_link = page.locator("a:has-text('深度学习'), a:has-text('Deep Learning'), a[href*='deep']")
        if dl_link.count() > 0:
            dl_link.first.click()
            expect(page).to_have_url(re.compile("deep|train", re.IGNORECASE))


class TestDeepLearningFlow:
    """深度学习流程测试 (新增)"""
    
    def test_training_page_loads(self, page: Page):
        """测试训练页面加载"""
        page.goto("http://localhost:80/deep-learning/train")
        expect(page.locator("body")).to_be_visible()
    
    def test_inference_page_loads(self, page: Page):
        """测试推理页面加载"""
        page.goto("http://localhost:80/deep-learning/inference")
        expect(page.locator("body")).to_be_visible()
    
    def test_model_management_page_loads(self, page: Page):
        """测试模型管理页面加载"""
        page.goto("http://localhost:80/deep-learning/models")
        expect(page.locator("body")).to_be_visible()
    
    def test_data_preprocessing_page_loads(self, page: Page):
        """测试数据预处理页面加载"""
        page.goto("http://localhost:80/deep-learning/preprocess")
        expect(page.locator("body")).to_be_visible()


class TestAIDAdviceFlow:
    """AI 建议流程测试"""
    
    def test_view_ai_advice(self, page: Page):
        """测试查看 AI 建议"""
        page.goto("http://localhost:80")
        # 检查是否有 AI 建议相关元素
        expect(page.locator(".ai-advice, .advice, .prediction")).to_be_visible(timeout=10000)


class TestNewsFlow:
    """新闻资讯流程测试"""
    
    def test_news_list_loads(self, page: Page):
        """测试新闻列表加载"""
        page.goto("http://localhost:80/news")
        expect(page.locator("body")).to_be_visible()
        expect(page.locator(".news-list, .news-item, article")).to_be_visible(timeout=10000)


class TestTechnicalIndicatorsFlow:
    """技术指标流程测试"""
    
    def test_technical_indicators_load(self, page: Page):
        """测试技术指标加载"""
        page.goto("http://localhost:80")
        # 检查是否有技术指标图表
        expect(page.locator(".indicator, .chart, .macd, .kdj, .rsi")).to_be_visible(timeout=10000)


class TestResponsiveDesign:
    """响应式设计测试"""
    
    def test_mobile_viewport(self, page: Page):
        """测试移动端视图"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:80")
        expect(page.locator("body")).to_be_visible()
    
    def test_tablet_viewport(self, page: Page):
        """测试平板视图"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("http://localhost:80")
        expect(page.locator("body")).to_be_visible()
    
    def test_desktop_viewport(self, page: Page):
        """测试桌面视图"""
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("http://localhost:80")
        expect(page.locator("body")).to_be_visible()


class TestAccessibility:
    """可访问性测试"""
    
    def test_page_has_title(self, page: Page):
        """测试页面有标题"""
        page.goto("http://localhost:80")
        expect(page.locator("h1, title")).to_be_visible()
    
    def test_images_have_alt_text(self, page: Page):
        """测试图片有 Alt 文本"""
        page.goto("http://localhost:80")
        images = page.locator("img")
        count = images.count()
        for i in range(min(count, 5)):  # 检查前 5 个图片
            img = images.nth(i)
            alt = img.get_attribute("alt")
            assert alt is not None, f"Image {i} missing alt text"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
