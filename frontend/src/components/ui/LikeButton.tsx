import { Heart } from 'lucide-react';
import { useState } from 'react';
import { likeReview, unlikeReview } from '../../lib/api';
import { useAuth } from '../../lib/auth';

interface LikeButtonProps {
  reviewId: number;
  initialLikeCount: number;
  initialLiked: boolean;
  onLikeChange?: (newCount: number, isLiked: boolean) => void;
}

export function LikeButton({ reviewId, initialLikeCount, initialLiked, onLikeChange }: LikeButtonProps) {
  const { user } = useAuth();
  const [likeCount, setLikeCount] = useState(initialLikeCount);
  const [liked, setLiked] = useState(initialLiked);
  const [loading, setLoading] = useState(false);

  const handleToggleLike = async () => {
    if (!user) {
      // Redirect to login or show toast
      alert('Please log in to like reviews');
      return;
    }

    setLoading(true);
    try {
      if (liked) {
        const response = await unlikeReview(reviewId);
        setLiked(false);
        setLikeCount(response.like_count);
        onLikeChange?.(response.like_count, false);
      } else {
        const response = await likeReview(reviewId);
        setLiked(true);
        setLikeCount(response.like_count);
        onLikeChange?.(response.like_count, true);
        
        // Show unlock notification if user unlocked a book
        if (response.unlocked_user_id === user.id) {
          // Could show a toast or modal here
          console.log('🎁 Congratulations! You unlocked this book with your top review!');
        }
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
      alert('Failed to update like. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleToggleLike}
      disabled={loading || !user}
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all
        ${liked
          ? 'bg-red-50 border-red-200 text-red-600'
          : 'bg-white border-gray-200 text-gray-600 hover:border-red-200 hover:text-red-600'
        }
        ${!user ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${loading ? 'opacity-50 cursor-wait' : ''}
      `}
      title={user ? (liked ? 'Unlike this review' : 'Like this review') : 'Login to like reviews'}
    >
      <Heart
        className={`w-4 h-4 ${liked ? 'fill-current' : ''}`}
        strokeWidth={liked ? 0 : 2}
      />
      <span className="text-sm font-medium">{likeCount}</span>
    </button>
  );
}
