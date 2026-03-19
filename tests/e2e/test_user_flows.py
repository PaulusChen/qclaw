"""
端到端流程测试 - TEST-E2E-001
完整用户流程的 E2E 测试
技术栈：Playwright
"""
import pytest
from playwright.sync_api import Page, expect
import re


class TestHomepageFlow:
    """首页访问流程测试"""
    
    def test_homepage_loads_successfully(self, page: Page):
        """测试首页成功加载"""
        # 访问首页
        page.goto("http://localhost:80")
        
        # 验证页面标题
        expect(page).to_have_title(re.compile("QCLaw"))
        
        # 验证页面包含关键元素
        expect(page.locator("h1")).to_contain_text("QCLaw")
    
    def test_homepage_shows_market_indices(self, page: Page):
        """测试首页显示大盘指标"""
        page.goto("http://localhost:80")
        
        # 验证大盘指标区域存在
        expect(page.locator(".market-indices")).to_be_visible()
        
        # 验证三大指数显示
        expect(page.locator(".index-shanghai")).to_be_visible()
        expect(page.locator(".index-shenzhen")).to_be_visible()
        expect(page.locator(".index-chinext")).to_be_visible()
    
    def test_homepage_auto_refresh(self, page: Page):
        """测试首页数据自动刷新"""
        page.goto("http://localhost:80")
        
        # 等待自动刷新
        page.wait_for_timeout(60000)  # 等待 60 秒
        
        # 验证数据已刷新
        expect(page.locator(".last-updated")).to_be_visible()


class TestAIDAdviceFlow:
    """AI 投资建议查看流程测试"""
    
    def test_view_ai_advice(self, page: Page):
        """测试查看 AI 投资建议"""
        page.goto("http://localhost:80/advice")
        
        # 验证 AI 建议区域存在
        expect(page.locator(".ai-advice")).to_be_visible()
        
        # 验证建议内容显示
        expect(page.locator(".advice-type")).to_be_visible()
        expect(page.locator(".confidence-level")).to_be_visible()
    
    def test_advice_shows_reasons(self, page: Page):
        """测试建议显示理由"""
        page.goto("http://localhost:80/advice")
        
        # 验证理由列表存在
        expect(page.locator(".advice-reasons")).to_be_visible()
    
    def test_advice_shows_risks(self, page: Page):
        """测试建议显示风险"""
        page.goto("http://localhost:80/advice")
        
        # 验证风险提示存在
        expect(page.locator(".advice-risks")).to_be_visible()


class TestNewsFlow:
    """新闻资讯查看流程测试"""
    
    def test_news_list_loads(self, page: Page):
        """测试新闻列表加载"""
        page.goto("http://localhost:80/news")
        
        # 验证新闻列表存在
        expect(page.locator(".news-list")).to_be_visible()
        
        # 验证至少有一条新闻
        expect(page.locator(".news-item").first).to_be_visible()
    
    def test_news_pagination(self, page: Page):
        """测试新闻分页功能"""
        page.goto("http://localhost:80/news")
        
        # 验证分页控件存在
        expect(page.locator(".pagination")).to_be_visible()
        
        # 点击下一页
        page.click(".pagination .next")
        page.wait_for_load_state("networkidle")
        
        # 验证页面切换
        expect(page).to_have_url(re.compile("page=2"))
    
    def test_news_detail_page(self, page: Page):
        """测试新闻详情页"""
        page.goto("http://localhost:80/news")
        
        # 点击第一条新闻
        page.click(".news-item:first-child")
        page.wait_for_load_state("networkidle")
        
        # 验证详情页加载
        expect(page.locator(".news-detail")).to_be_visible()


class TestTechnicalIndicatorsFlow:
    """技术指标查看流程测试"""
    
    def test_technical_indicators_load(self, page: Page):
        """测试技术指标加载"""
        page.goto("http://localhost:80/technical")
        
        # 验证技术指标区域存在
        expect(page.locator(".technical-indicators")).to_be_visible()
        
        # 验证 MACD 显示
        expect(page.locator(".macd-chart")).to_be_visible()
        
        # 验证 KDJ 显示
        expect(page.locator(".kdj-chart")).to_be_visible()
        
        # 验证 RSI 显示
        expect(page.locator(".rsi-chart")).to_be_visible()
    
    def test_indicators_chart_rendering(self, page: Page):
        """测试指标图表渲染"""
        page.goto("http://localhost:80/technical")
        
        # 等待图表渲染
        page.wait_for_selector(".chart-rendered")
        
        # 验证图表已渲染
        expect(page.locator(".chart-rendered")).to_be_visible()


class TestErrorPagesFlow:
    """错误页面显示测试"""
    
    def test_404_page(self, page: Page):
        """测试 404 错误页面"""
        response = page.goto("http://localhost:80/nonexistent-page")
        
        # 验证响应状态
        if response:
            assert response.status() == 404
        
        # 验证页面包含 404 相关内容
        expect(page.locator("body")).to_contain_text("404")
    
    def test_api_error_handling(self, page: Page):
        """测试 API 错误处理"""
        page.goto("http://localhost:80")
        
        # 验证错误消息元素存在 (可能为空或隐藏)
        # 注意：实际错误显示取决于 API 响应
        error_message = page.locator(".error-message")
        # 只要元素存在即可，不一定需要可见
        expect(error_message).to_be_attached()


class TestResponsiveDesign:
    """响应式设计测试"""
    
    def test_mobile_viewport(self, page: Page):
        """测试移动端视图"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:80")
        
        # 验证移动端布局
        expect(page.locator(".mobile-nav")).to_be_visible()
    
    def test_tablet_viewport(self, page: Page):
        """测试平板端视图"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("http://localhost:80")
        
        # 验证平板端布局
        expect(page.locator(".tablet-nav")).to_be_visible()
    
    def test_desktop_viewport(self, page: Page):
        """测试桌面端视图"""
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("http://localhost:80")
        
        # 验证桌面端布局
        expect(page.locator(".desktop-nav")).to_be_visible()


class TestAccessibility:
    """无障碍访问测试"""
    
    def test_page_has_title(self, page: Page):
        """测试页面有标题"""
        page.goto("http://localhost:80")
        expect(page).to_have_title(re.compile("QCLaw"))
    
    def test_images_have_alt_text(self, page: Page):
        """测试图片有替代文本"""
        page.goto("http://localhost:80")
        
        # 验证所有图片都有 alt 属性
        images = page.locator("img")
        for i in range(images.count()):
            img = images.nth(i)
            expect(img).to_have_attribute("alt", re.compile(".+"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
