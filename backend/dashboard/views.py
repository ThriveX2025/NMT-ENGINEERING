from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .utils import read_excel_data, get_excel_info, get_excel_stats, update_remark

class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard operations
    Reads data directly from Excel file
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        excel_info = get_excel_info()
        
        if excel_info and 'error' not in excel_info:
            return Response({
                'total_records': excel_info.get('total_rows', 0),
                'total_columns': len(excel_info.get('columns', [])),
                'columns': excel_info.get('columns', []),
                'last_modified': excel_info.get('last_modified', 'Unknown'),
                'file_name': 'DATA_V2.xlsx',
            })
        else:
            return Response({
                'error': 'Excel file not found or error reading file',
                'details': excel_info,
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def data(self, request):
        """Get Excel data"""
        try:
            # Get limit from query params (default 100)
            limit = request.query_params.get('limit', 100)
            try:
                limit = int(limit)
            except ValueError:
                limit = 100
            
            data = read_excel_data(limit=limit)
            
            return Response({
                'count': len(data),
                'data': data,
            })
        except FileNotFoundError as e:
            return Response({
                'error': str(e),
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def detailed_stats(self, request):
        """Get detailed statistics from Excel"""
        try:
            stats = get_excel_stats()
            return Response(stats)
        except Exception as e:
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_remark(self, request):
        """Update remark for a specific row"""
        try:
            row_index = request.data.get('row_index')
            remark_value = request.data.get('remark_value')
            
            # Debug logging
            print(f"Received request data: {request.data}")
            print(f"row_index: {row_index} (type: {type(row_index)})")
            print(f"remark_value: {remark_value} (type: {type(remark_value)})")
            
            if row_index is None or remark_value is None:
                return Response({
                    'error': 'row_index and remark_value are required',
                    'received': {'row_index': row_index, 'remark_value': remark_value}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = update_remark(int(row_index), remark_value)
            
            if result['success']:
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in update_remark: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
