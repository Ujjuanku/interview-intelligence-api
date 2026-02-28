import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.schemas.resume import UploadResponse, SearchResponse, SearchChunk
from app.schemas.question import QuestionRequest, QuestionResponse
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.schemas.auditor import AuditRequest, AuditResponse
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.chunking import chunk_text
from app.services.embeddings import get_embeddings
from app.services.faiss_store import faiss_store
from app.services.question_agent import generate_interview_questions
from app.services.evaluation_agent import evaluate_candidate_answer
from app.services.auditor_agent import audit_evaluation
from app.services.decision_agent import make_hiring_decision

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
            
        chunks = chunk_text(text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks generated from text.")
            
        embeddings = await get_embeddings(chunks)
        
        metadatas = [
            {"filename": file.filename, "text": chunk, "chunk_index": i} 
            for i, chunk in enumerate(chunks)
        ]
        
        faiss_store.add_vectors(embeddings, metadatas)
        
        return UploadResponse(
            filename=file.filename,
            num_chunks=len(chunks),
            message="Resume successfully ingested and indexed."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=SearchResponse)
async def search_resume(query: str = Query(..., min_length=1), top_k: int = Query(5, ge=1, le=20)):
    try:
        query_embedding = (await get_embeddings([query]))[0]
        results = faiss_store.search(query_embedding, top_k=top_k)
        
        search_chunks = [
            SearchChunk(
                text=metadata.get("text", ""),
                metadata={"filename": metadata.get("filename", ""), "chunk_index": metadata.get("chunk_index", -1)},
                score=score
            )
            for metadata, score in results
        ]
        
        return SearchResponse(query=query, results=search_chunks)
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    try:
        response = await generate_interview_questions(request.role)
        return response
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questions. Please try again.")

@router.post("/evaluate-answer", response_model=EvaluationResponse)
async def evaluate_answer(request: EvaluationRequest):
    try:
        response = await evaluate_candidate_answer(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate answer. Please try again.")

@router.post("/audit-evaluation", response_model=AuditResponse)
async def audit_eval(request: AuditRequest):
    try:
        response = await audit_evaluation(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing evaluation audit: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete audit. Please try again.")

@router.post("/make-decision", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    try:
        response = await make_hiring_decision(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing hiring decision aggregation: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete decision evaluation. Please try again.")


