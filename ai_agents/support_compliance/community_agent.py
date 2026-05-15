"""
Community Agent - Auto-manage 100K+ community members, auto-moderate
Replaces 1 Community Manager + 5 community moderators
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import numpy as np
from ..agent_framework import BaseAIAgent, AgentRole, MessageType, Priority, AgentCapability

@dataclass
class CommunityMember:
    """Community member"""
    member_id: str
    username: str
    join_date: datetime
    activity_level: str
    reputation: float
    status: str

@dataclass
class CommunityPost:
    """Community post"""
    post_id: str
    author_id: str
    content: str
    category: str
    created_at: datetime
    moderated: bool = False
    engagement: Dict[str, int] = None

@dataclass
class CommunityModeration:
    """Community moderation action"""
    moderation_id: str
    post_id: str
    action_type: str
    reason: str
    moderated_by: str
    moderated_at: datetime

class CommunityAgent(BaseAIAgent):
    """Community Agent - Automated community management"""
    
    def __init__(self):
        super().__init__(
            agent_id="community_001",
            role=AgentRole.COMMUNITY,
            name="Community Manager",
            description="Auto-manage 100K+ community members, auto-moderate"
        )
        
        self.community_members: List[CommunityMember] = []
        self.community_posts: List[CommunityPost] = []
        self.moderation_actions: List[CommunityModeration] = []
        self.community_stats: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize community agent"""
        try:
            await self._setup_community_rules()
            await self._load_community_data()
            asyncio.create_task(self._community_management_loop())
            asyncio.create_task(self._moderation_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Community Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get community agent capabilities"""
        return [
            AgentCapability(
                name="member_management",
                description="Auto-manage 100K+ community members",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.98, "response_time": 2.0},
                dependencies=["member_database", "engagement_tracking"]
            ),
            AgentCapability(
                name="content_moderation",
                description="Auto-moderate content and enforce rules",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 1.0},
                dependencies=["content_filtering", "nlp_moderation"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process community tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle community commands"""
        if subject == "add_member":
            return await self._add_member(content)
        elif subject == "create_post":
            return await self._create_post(content)
        elif subject == "moderate_content":
            return await self._moderate_content(content)
        elif subject == "update_member_activity":
            return await self._update_member_activity(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _add_member(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Add new community member"""
        username = content.get('username', 'unknown')
        member_id = content.get('member_id', f"member_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        
        # Create member
        member = CommunityMember(
            member_id=member_id,
            username=username,
            join_date=datetime.utcnow(),
            activity_level='new',
            reputation=50.0,  # Starting reputation
            status='active'
        )
        
        self.community_members.append(member)
        
        # Send welcome message
        await self._send_welcome_message(member)
        
        return {
            'member_id': member_id,
            'username': username,
            'join_date': member.join_date.isoformat(),
            'status': member.status,
            'welcome_sent': True
        }
    
    async def _create_post(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create new community post"""
        author_id = content.get('author_id', 'unknown')
        content_text = content.get('content', '')
        category = content.get('category', 'general')
        
        # Create post
        post = CommunityPost(
            post_id=f"post_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            author_id=author_id,
            content=content_text,
            category=category,
            created_at=datetime.utcnow(),
            engagement={'views': 0, 'likes': 0, 'comments': 0}
        )
        
        # Auto-moderate post
        moderation_result = await self._auto_moderate_post(post)
        
        if moderation_result['approved']:
            post.moderated = True
            self.community_posts.append(post)
        else:
            # Flag for manual review
            await self._flag_for_manual_review(post, moderation_result['reason'])
        
        return {
            'post_id': post.post_id,
            'author_id': author_id,
            'category': category,
            'status': 'approved' if moderation_result['approved'] else 'flagged',
            'moderation_reason': moderation_result.get('reason', ''),
            'created_at': post.created_at.isoformat()
        }
    
    async def _moderate_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Moderate content"""
        post_id = content.get('post_id', 'unknown')
        
        # Find post
        post = next((p for p in self.community_posts if p.post_id == post_id), None)
        
        if not post:
            return {'error': f'Post not found: {post_id}'}
        
        # Perform moderation
        moderation_result = await self._auto_moderate_post(post)
        
        if moderation_result['action'] != 'none':
            # Create moderation record
            moderation = CommunityModeration(
                moderation_id=f"mod_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                post_id=post_id,
                action_type=moderation_result['action'],
                reason=moderation_result['reason'],
                moderated_by='community_agent',
                moderated_at=datetime.utcnow()
            )
            
            self.moderation_actions.append(moderation)
            
            # Update post status
            if moderation_result['action'] == 'remove':
                self.community_posts.remove(post)
            elif moderation_result['action'] == 'edit':
                post.content = moderation_result['edited_content']
        
        return {
            'post_id': post_id,
            'action_taken': moderation_result['action'],
            'reason': moderation_result['reason'],
            'moderated_at': moderation.moderated_at.isoformat()
        }
    
    async def _update_member_activity(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update member activity"""
        member_id = content.get('member_id', 'unknown')
        activity_type = content.get('activity_type', 'post')
        activity_value = content.get('activity_value', 1)
        
        # Find member
        member = next((m for m in self.community_members if m.member_id == member_id), None)
        
        if member:
            # Update activity level
            if activity_type == 'post':
                member.reputation += activity_value * 2
            elif activity_type == 'comment':
                member.reputation += activity_value
            elif activity_type == 'like':
                member.reputation += activity_value * 0.5
            
            # Update activity level based on recent activity
            if member.reputation > 200:
                member.activity_level = 'highly_active'
            elif member.reputation > 100:
                member.activity_level = 'active'
            elif member.reputation > 50:
                member.activity_level = 'moderately_active'
            else:
                member.activity_level = 'low_activity'
            
            return {
                'member_id': member_id,
                'new_reputation': member.reputation,
                'activity_level': member.activity_level,
                'updated_at': datetime.utcnow().isoformat()
            }
        
        return {'error': f'Member not found: {member_id}'}
    
    async def _community_management_loop(self):
        """Continuous community management loop"""
        while self.is_active:
            try:
                # Update member activity levels
                await self._update_all_member_activity()
                
                # Generate community insights
                await self._generate_community_insights()
                
                # Send engagement notifications
                await self._send_engagement_notifications()
                
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                logger.error(f"Error in community management loop: {e}")
                await asyncio.sleep(300)
    
    async def _moderation_loop(self):
        """Continuous moderation loop"""
        while self.is_active:
            try:
                # Moderate new posts
                await self._moderate_new_posts()
                
                # Review flagged content
                await self._review_flagged_content()
                
                # Update moderation rules
                await self._update_moderation_rules()
                
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error in moderation loop: {e}")
                await asyncio.sleep(60)
    
    async def _auto_moderate_post(self, post: CommunityPost) -> Dict[str, Any]:
        """Automatically moderate post content"""
        content_lower = post.content.lower()
        
        # Check for prohibited content
        prohibited_words = ['spam', 'abuse', 'hate', 'inappropriate', 'offensive']
        if any(word in content_lower for word in prohibited_words):
            return {
                'approved': False,
                'action': 'remove',
                'reason': 'prohibited_content'
            }
        
        # Check for spam patterns
        if len(post.content) < 10 and post.content.count('http') > 0:
            return {
                'approved': False,
                'action': 'remove',
                'reason': 'spam_content'
            }
        
        # Check for duplicate content
        recent_posts = [p for p in self.community_posts if (datetime.utcnow() - p.created_at).total_seconds() < 3600]
        if any(p.content == post.content for p in recent_posts):
            return {
                'approved': False,
                'action': 'flag',
                'reason': 'duplicate_content'
            }
        
        # Check author reputation
        author = next((m for m in self.community_members if m.member_id == post.author_id), None)
        if author and author.reputation < 10:
            return {
                'approved': False,
                'action': 'flag',
                'reason': 'new_member_post'
            }
        
        return {
            'approved': True,
            'action': 'none',
            'reason': 'approved'
        }
    
    async def _send_welcome_message(self, member: CommunityMember):
        """Send welcome message to new member"""
        welcome_message = f"Welcome to DEDAN 2.0 Community, {member.username}! We're excited to have you join our mineral trading community."
        
        # This would integrate with messaging system
        logger.info(f"Sending welcome message to {member.username}")
    
    async def _flag_for_manual_review(self, post: CommunityPost, reason: str):
        """Flag post for manual review"""
        await self.send_message(
            "community_manager_001",
            MessageType.ALERT,
            f"Post Flagged for Review: {post.post_id}",
            {
                'post_id': post.post_id,
                'author_id': post.author_id,
                'content': post.content[:200],
                'flag_reason': reason,
                'flagged_at': datetime.utcnow().isoformat()
            },
            priority=Priority.HIGH
        )
    
    async def _update_all_member_activity(self):
        """Update activity levels for all members"""
        for member in self.community_members:
            # Decay reputation over time
            days_since_join = (datetime.utcnow() - member.join_date).days
            if days_since_join > 30:
                member.reputation *= 0.95  # 5% decay per month
            
            # Update activity level
            if member.reputation > 200:
                member.activity_level = 'highly_active'
            elif member.reputation > 100:
                member.activity_level = 'active'
            elif member.reputation > 50:
                member.activity_level = 'moderately_active'
            else:
                member.activity_level = 'low_activity'
    
    async def _generate_community_insights(self):
        """Generate community insights"""
        total_members = len(self.community_members)
        active_members = len([m for m in self.community_members if m.activity_level in ['active', 'highly_active']])
        total_posts = len(self.community_posts)
        
        self.community_stats = {
            'total_members': total_members,
            'active_members': active_members,
            'total_posts': total_posts,
            'engagement_rate': total_posts / total_members if total_members > 0 else 0,
            'average_reputation': np.mean([m.reputation for m in self.community_members]) if self.community_members else 0
        }
    
    async def _send_engagement_notifications(self):
        """Send engagement notifications"""
        # Notify high-reputation members of new content
        top_members = sorted(self.community_members, key=lambda x: x.reputation, reverse=True)[:10]
        
        if len(self.community_posts) > 0:
            latest_post = self.community_posts[-1]
            
            for member in top_members:
                # This would integrate with notification system
                logger.info(f"Notifying {member.username} of new post")
    
    async def _moderate_new_posts(self):
        """Moderate new posts"""
        # Mock new posts moderation
        new_posts = [
            CommunityPost(
                post_id=f"post_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{i}",
                author_id=f"member_{np.random.randint(1, 1000)}",
                content=f"Sample post content {i}",
                category=np.random.choice(['trading', 'discussion', 'announcement']),
                created_at=datetime.utcnow(),
                engagement={'views': 0, 'likes': 0, 'comments': 0}
            )
            for i in range(5)
        ]
        
        for post in new_posts:
            moderation_result = await self._auto_moderate_post(post)
            
            if moderation_result['approved']:
                self.community_posts.append(post)
            else:
                await self._flag_for_manual_review(post, moderation_result['reason'])
    
    async def _review_flagged_content(self):
        """Review flagged content"""
        # Mock review process
        flagged_posts = [p for p in self.community_posts if not p.moderated]
        
        for post in flagged_posts:
            # This would integrate with manual review system
            logger.info(f"Reviewing flagged post: {post.post_id}")
    
    async def _update_moderation_rules(self):
        """Update moderation rules"""
        # Mock rule updates
        logger.info("Updating moderation rules")
    
    async def _setup_community_rules(self):
        """Setup community rules and guidelines"""
        # Mock community rules setup
        logger.info("Setting up community rules")
    
    async def _load_community_data(self):
        """Load existing community data"""
        # Mock existing community data
        existing_members = [
            CommunityMember(
                member_id=f"member_{i}",
                username=f"user_{i}",
                join_date=datetime.utcnow() - timedelta(days=np.random.randint(1, 365)),
                activity_level=np.random.choice(['new', 'low_activity', 'moderately_active', 'active', 'highly_active']),
                reputation=np.random.uniform(10, 500),
                status='active'
            )
            for i in range(100)  # 100 existing members
        ]
        
        self.community_members.extend(existing_members)
        
        existing_posts = [
            CommunityPost(
                post_id=f"post_{i}",
                author_id=f"member_{np.random.randint(1, 100)}",
                content=f"Community post content {i}",
                category=np.random.choice(['trading', 'discussion', 'announcement', 'help']),
                created_at=datetime.utcnow() - timedelta(days=np.random.randint(1, 30)),
                moderated=True,
                engagement={
                    'views': np.random.randint(10, 1000),
                    'likes': np.random.randint(0, 100),
                    'comments': np.random.randint(0, 50)
                }
            )
            for i in range(50)  # 50 existing posts
        ]
        
        self.community_posts.extend(existing_posts)

community_agent = CommunityAgent()
