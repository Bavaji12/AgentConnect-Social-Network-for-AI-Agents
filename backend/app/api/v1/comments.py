from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentApprovalUpdate, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.patch("/{comment_id}/approval", response_model=CommentResponse)
def update_comment_approval(
    comment_id: str,
    update: CommentApprovalUpdate,
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    comment.approval_status = update.approval_status
    db.commit()
    db.refresh(comment)

    resp = CommentResponse.model_validate(comment)
    resp.author_company = comment.author_agent.company_name if comment.author_agent else "Unknown"
    resp.author_name = comment.author_agent.agent_name if comment.author_agent else "Unknown"
    return resp

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
    db.delete(comment)
    db.commit()
    return None
