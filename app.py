import streamlit as st
import pandas as pd
import io
import json
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="CSV Organizer Pro", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# カスタムCSS
st.markdown("""
<style>
/* メインタイトル */
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 2rem;
}

/* セクションヘッダー */
.section-header {
    font-size: 1.3rem;
    font-weight: 600;
    color: #2c3e50;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e8f4f8;
}

/* カード風コンテナ */
.card-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border: 1px solid #e8f4f8;
    margin-bottom: 1rem;
}

/* ステータスバッジ */
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    margin: 0.25rem;
}

.status-success {
    background: #d4edda;
    color: #155724;
}

.status-warning {
    background: #fff3cd;
    color: #856404;
}

.status-info {
    background: #d1ecf1;
    color: #0c5460;
}

/* ボタンスタイル */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
}

/* メトリクスカード */
.metric-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    border: 1px solid #dee2e6;
}

/* アップロードエリア */
.upload-area {
    border: 2px dashed #cbd5e0;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    background: #f8fafc;
    transition: all 0.3s ease;
}

/* ファイル情報 */
.file-info {
    background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
    border-radius: 8px;
    padding: 1rem;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}

/* 操作タブ */
.operation-tab {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    border: 1px solid #e9ecef;
}

/* チェックボックスグリッド */
.checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 0.5rem;
    margin: 1rem 0;
}

/* プレビューテーブル */
.preview-table {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* サイドバーセクション */
.sidebar-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    border: 1px solid #e9ecef;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
    .main-title {
        font-size: 2rem;
    }
    .section-header {
        font-size: 1.1rem;
    }
}

/* デバッグ情報を非表示 */
.stDeployButton {
    display: none;
}

/* エラー表示の改善 */
.stAlert {
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化関数
def init_session_state():
    """セッション状態を安全に初期化"""
    try:
        if 'df' not in st.session_state:
            st.session_state.df = None
        if 'original_columns' not in st.session_state:
            st.session_state.original_columns = []
        if 'selected_columns' not in st.session_state:
            st.session_state.selected_columns = set()
        if 'column_order' not in st.session_state:
            st.session_state.column_order = []
        if 'uploaded_file_name' not in st.session_state:
            st.session_state.uploaded_file_name = None
        if 'templates' not in st.session_state:
            st.session_state.templates = {}
        if 'mode' not in st.session_state:
            st.session_state.mode = "manual"
        if 'current_operation' not in st.session_state:
            st.session_state.current_operation = "merge"
    except Exception as e:
        # エラーが発生した場合は静かに処理
        pass

# テンプレート保存機能
def save_template(name, config):
    """テンプレートを保存"""
    try:
        st.session_state.templates[name] = {
            'config': config,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'description': config.get('description', '')
        }
    except Exception as e:
        st.error(f"テンプレート保存エラー: {str(e)}")

# テンプレート適用機能
def apply_template(template_config, df):
    """テンプレートを適用"""
    try:
        # 結合処理
        for merge_op in template_config.get('merge_operations', []):
            if all(col in df.columns for col in merge_op['columns']):
                new_col = merge_op['new_column']
                separator = merge_op.get('separator', '')
                if separator:
                    df[new_col] = df[merge_op['columns']].apply(
                        lambda row: separator.join([str(val) for val in row if str(val).strip()]), axis=1
                    )
                else:
                    df[new_col] = df[merge_op['columns']].apply(
                        lambda row: ''.join([str(val) for val in row if str(val).strip()]), axis=1
                    )
        
        # 分割処理
        for split_op in template_config.get('split_operations', []):
            if split_op['column'] in df.columns:
                split_data = df[split_op['column']].str.split(split_op['delimiter'], expand=True)
                for i, new_col in enumerate(split_op['new_columns']):
                    if i < split_data.shape[1]:
                        df[new_col] = split_data[i].fillna('')
        
        # 空列追加
        for empty_col in template_config.get('empty_columns', []):
            if empty_col not in df.columns:
                df[empty_col] = ''
        
        # 列順序と選択を適用
        available_columns = [col for col in template_config.get('column_order', []) if col in df.columns]
        selected_columns = set(col for col in template_config.get('selected_columns', []) if col in df.columns)
        
        return df, available_columns, selected_columns
    except Exception as e:
        st.error(f"テンプレート適用エラー: {str(e)}")
        return df, [], set()

# メインアプリケーション
def main():
    # セッション状態初期化
    init_session_state()
    
    # メインタイトル
    st.markdown('<h1 class="main-title">📊 CSV Organizer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">高度な CSV データ整理・変換ツール</p>', unsafe_allow_html=True)
    
    # モード選択（サイドバー）
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-top: 0;">🎯 処理モード</h3>', unsafe_allow_html=True)
        mode = st.radio(
            "処理方法を選択",
            ["🔧 手動設定", "⚡ テンプレート適用"],
            index=0 if st.session_state.mode == "manual" else 1,
            help="手動設定: 一から設定を行う\nテンプレート適用: 保存済み設定を使用"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.mode = "manual" if mode == "🔧 手動設定" else "template"
    
    # ファイルアップロードセクション
    st.markdown('<div class="section-header">📁 ファイルアップロード</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "CSVまたはExcelファイルを選択してください", 
            type=["csv", "xlsx", "xls"],
            help="対応形式: CSV, Excel (.xlsx, .xls)"
        )
    with col2:
        if uploaded_file:
            st.markdown(f'''
            <div class="file-info">
                <strong>📄 {uploaded_file.name}</strong><br>
                <small>サイズ: {uploaded_file.size / 1024:.1f} KB</small>
            </div>
            ''', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # 新しいファイルがアップロードされた場合、状態をリセット
        if st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.df = None
            if st.session_state.mode == "manual":
                st.session_state.selected_columns = set()
                st.session_state.column_order = []
                st.session_state.original_columns = []
        
        # 読み込み設定
        with st.expander("⚙️ 詳細設定", expanded=False):
            header_row = st.number_input(
                "ヘッダー行番号 (0から開始)", 
                min_value=0, 
                max_value=20, 
                value=0,
                help="データのヘッダー行が何行目にあるかを指定"
            )
        
        # ファイル読み込み
        try:
            with st.spinner('📊 データを読み込んでいます...'):
                file_content = uploaded_file.getvalue()
                
                if uploaded_file.name.lower().endswith('.csv'):
                    # CSV読み込み（エンコーディング自動判定）
                    try:
                        df = pd.read_csv(io.BytesIO(file_content), header=header_row, encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            df = pd.read_csv(io.BytesIO(file_content), header=header_row, encoding='cp932')
                        except UnicodeDecodeError:
                            df = pd.read_csv(io.BytesIO(file_content), header=header_row, encoding='shift-jis')
                else:
                    # Excel読み込み
                    df = pd.read_excel(io.BytesIO(file_content), header=header_row)
                
                # 列名の重複を処理
                if df.columns.duplicated().any():
                    cols = pd.Series(df.columns)
                    for dup in cols[cols.duplicated()].unique():
                        cols[cols[cols == dup].index.values.tolist()] = [dup + f'_{i}' if i != 0 else dup for i in range(sum(cols == dup))]
                    df.columns = cols.tolist()
                
                # データ型の最適化
                df = df.fillna('')
                
                # 成功メッセージ
                st.success(f"✅ ファイル読み込み完了！ {len(df):,} 行 × {len(df.columns)} 列")
            
            # テンプレートモードの場合
            if st.session_state.mode == "template" and st.session_state.templates:
                st.markdown('<div class="section-header">⚡ テンプレート適用</div>', unsafe_allow_html=True)
                
                template_names = list(st.session_state.templates.keys())
                selected_template = st.selectbox(
                    "適用するテンプレートを選択",
                    options=["── 選択してください ──"] + template_names,
                    key="template_selector"
                )
                
                if selected_template != "── 選択してください ──":
                    template_info = st.session_state.templates[selected_template]
                    
                    # テンプレート情報表示
                    st.markdown(f'''
                    <div class="card-container">
                        <h4>📋 {selected_template}</h4>
                        <p><strong>説明:</strong> {template_info['description'] or 'なし'}</p>
                        <p><small><strong>作成日時:</strong> {template_info['created_at']}</small></p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button("⚡ テンプレート適用", type="primary", use_container_width=True):
                            with st.spinner('🔄 テンプレートを適用しています...'):
                                df, column_order, selected_columns = apply_template(template_info['config'], df)
                                st.session_state.df = df
                                st.session_state.column_order = column_order
                                st.session_state.selected_columns = selected_columns
                                st.success("✅ テンプレートを適用しました")
                                st.rerun()
            
            # 手動モードまたは初回読み込み時の設定
            if st.session_state.mode == "manual" or not st.session_state.original_columns:
                st.session_state.df = df
                if not st.session_state.original_columns:
                    st.session_state.original_columns = list(df.columns)
                    st.session_state.column_order = list(df.columns)
        
        except Exception as e:
            st.error(f"❌ ファイル読み込みエラー: {str(e)}")
            return
        
        # データプレビュー
        with st.expander("📋 データプレビュー", expanded=False):
            st.markdown('<div class="preview-table">', unsafe_allow_html=True)
            st.dataframe(df.head(10), use_container_width=True, height=300)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 統計情報
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #2c3e50; margin: 0;">{len(df):,}</h3>
                    <p style="margin: 0; color: #666;">総行数</p>
                </div>
                ''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #2c3e50; margin: 0;">{len(df.columns)}</h3>
                    <p style="margin: 0; color: #666;">総列数</p>
                </div>
                ''', unsafe_allow_html=True)
            with col3:
                memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #2c3e50; margin: 0;">{memory_usage:.1f} MB</h3>
                    <p style="margin: 0; color: #666;">メモリ使用量</p>
                </div>
                ''', unsafe_allow_html=True)
            with col4:
                null_count = df.isnull().sum().sum()
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #2c3e50; margin: 0;">{null_count:,}</h3>
                    <p style="margin: 0; color: #666;">欠損値数</p>
                </div>
                ''', unsafe_allow_html=True)
        
        # 手動モードの場合の列操作
        if st.session_state.mode == "manual":
            st.markdown('<div class="section-header">🔧 データ操作</div>', unsafe_allow_html=True)
            
            # 操作タブ
            tab_col1, tab_col2, tab_col3 = st.columns(3)
            
            with tab_col1:
                if st.button("🔗 列結合", use_container_width=True):
                    st.session_state.current_operation = "merge"
            with tab_col2:
                if st.button("✂️ 列分割", use_container_width=True):
                    st.session_state.current_operation = "split"
            with tab_col3:
                if st.button("➕ 空列追加", use_container_width=True):
                    st.session_state.current_operation = "empty"
            
            # 現在の操作を表示
            current_op = st.session_state.current_operation
            
            if current_op == "merge":
                st.markdown('<div class="operation-tab">', unsafe_allow_html=True)
                st.markdown("#### 🔗 列結合")
                
                merge_columns = st.multiselect(
                    "結合する列を選択", 
                    options=list(df.columns),
                    help="複数の列を1つにまとめます"
                )
                
                if merge_columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_column_name = st.text_input("結合後の列名", value="結合列", key="merge_name")
                    with col2:
                        separator = st.text_input("区切り文字", value="", placeholder="空欄=直接結合", key="merge_sep")
                    
                    if st.button("🔗 結合実行", type="primary", key="merge_execute"):
                        if new_column_name and new_column_name not in df.columns:
                            # 列結合実行
                            if separator:
                                df[new_column_name] = df[merge_columns].apply(
                                    lambda row: separator.join([str(val) for val in row if str(val).strip()]), axis=1
                                )
                            else:
                                df[new_column_name] = df[merge_columns].apply(
                                    lambda row: ''.join([str(val) for val in row if str(val).strip()]), axis=1
                                )
                            
                            st.session_state.df = df
                            st.session_state.column_order.append(new_column_name)
                            st.session_state.selected_columns.add(new_column_name)
                            
                            st.success(f"✅ 列 '{new_column_name}' を作成しました")
                            st.rerun()
                        else:
                            st.error("❌ 有効な列名を入力してください（重複不可）")
                st.markdown('</div>', unsafe_allow_html=True)
    
            elif current_op == "split":
                st.markdown('<div class="operation-tab">', unsafe_allow_html=True)
                st.markdown("#### ✂️ 列分割")
                
                split_column = st.selectbox(
                    "分割する列を選択", 
                    options=["── 選択してください ──"] + list(df.columns),
                    key="split_col_select"
                )
                
                if split_column != "── 選択してください ──":
                    col1, col2 = st.columns(2)
                    with col1:
                        delimiter = st.text_input("区切り文字", value=" ", help="例: 半角スペース、カンマ、ハイフンなど", key="split_delim")
                    with col2:
                        new_column_names = st.text_input(
                            "新しい列名（カンマ区切り）", 
                            value="分割列1,分割列2",
                            help="例: 姓,名",
                            key="split_names"
                        )
                    
                    if st.button("✂️ 分割実行", type="primary", key="split_execute"):
                        if delimiter and new_column_names:
                            names = [name.strip() for name in new_column_names.split(',') if name.strip()]
                            if names:
                                split_data = df[split_column].str.split(delimiter, expand=True)
                                
                                added_columns = []
                                for i, name in enumerate(names):
                                    if i < split_data.shape[1] and name not in df.columns:
                                        df[name] = split_data[i].fillna('')
                                        st.session_state.column_order.append(name)
                                        st.session_state.selected_columns.add(name)
                                        added_columns.append(name)
                                
                                if added_columns:
                                    st.session_state.df = df
                                    st.success(f"✅ 列 '{split_column}' を {len(added_columns)} 個の列に分割しました")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ 新しい列が作成されませんでした")
                st.markdown('</div>', unsafe_allow_html=True)
    
            elif current_op == "empty":
                st.markdown('<div class="operation-tab">', unsafe_allow_html=True)
                st.markdown("#### ➕ 空列追加")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    empty_column_names = st.text_input(
                        "追加する空列名（カンマ区切り）", 
                        placeholder="例: 備考,メモ,確認状況",
                        key="empty_names"
                    )
                with col2:
                    st.write("")  # スペース
                    if st.button("➕ 追加実行", type="primary", key="empty_execute"):
                        if empty_column_names:
                            names = [name.strip() for name in empty_column_names.split(',') if name.strip()]
                            added_count = 0
                            added_names = []
                            for name in names:
                                if name not in df.columns:
                                    df[name] = ''
                                    st.session_state.column_order.append(name)
                                    st.session_state.selected_columns.add(name)
                                    added_count += 1
                                    added_names.append(name)
                            
                            if added_count > 0:
                                st.session_state.df = df
                                st.success(f"✅ {added_count} 個の空列を追加しました")
                                st.rerun()
                            else:
                                st.warning("⚠️ 追加できる新しい列がありませんでした")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 列選択セクション
        st.markdown('<div class="section-header">🎯 出力列の選択</div>', unsafe_allow_html=True)
        
        # 全選択・全解除ボタン
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("☑️ 全選択", key="select_all", use_container_width=True):
                st.session_state.selected_columns = set(st.session_state.column_order)
                st.rerun()
        with col2:
            if st.button("☐ 全解除", key="deselect_all", use_container_width=True):
                st.session_state.selected_columns = set()
                st.rerun()
        with col3:
            st.markdown(f'<span class="status-badge status-info">選択中: {len(st.session_state.selected_columns)} / {len(st.session_state.column_order)} 列</span>', unsafe_allow_html=True)
        
        # 列選択チェックボックス（改良版）
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        columns_per_row = 2
        column_chunks = [st.session_state.column_order[i:i + columns_per_row] 
                        for i in range(0, len(st.session_state.column_order), columns_per_row)]
        
        for chunk in column_chunks:
            cols = st.columns(len(chunk))
            for i, column_name in enumerate(chunk):
                with cols[i]:
                    # サンプル値の取得
                    try:
                        if len(df) > 0 and column_name in df.columns:
                            sample_value = str(df[column_name].iloc[0])
                            if len(sample_value) > 20:
                                sample_text = f"{sample_value[:20]}..."
                            else:
                                sample_text = sample_value if sample_value else "(空)"
                        else:
                            sample_text = "(空)"
                    except:
                        sample_text = "(エラー)"
                    
                    is_selected = st.checkbox(
                        f"**{column_name}**",
                        value=column_name in st.session_state.selected_columns,
                        key=f"cb_{column_name}",
                        help=f"サンプル値: {sample_text}"
                    )
                    
                    if is_selected:
                        st.session_state.selected_columns.add(column_name)
                    else:
                        st.session_state.selected_columns.discard(column_name)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 列順序調整
        if len(st.session_state.selected_columns) > 1:
            with st.expander("🔄 列順序の調整", expanded=False):
                selected_in_order = [col for col in st.session_state.column_order 
                                   if col in st.session_state.selected_columns]
                
                st.markdown("**現在の列順序:**")
                for i, col in enumerate(selected_in_order, 1):
                    col1, col2, col3 = st.columns([6, 1, 1])
                    with col1:
                        st.write(f"{i}. **{col}**")
                    with col2:
                        if i > 1:
                            if st.button("⬆️", key=f"up_{col}", help="上に移動"):
                                new_order = selected_in_order.copy()
                                new_order[i-1], new_order[i-2] = new_order[i-2], new_order[i-1]
                                unselected = [col for col in st.session_state.column_order 
                                            if col not in st.session_state.selected_columns]
                                st.session_state.column_order = new_order + unselected
                                st.rerun()
                    with col3:
                        if i < len(selected_in_order):
                            if st.button("⬇️", key=f"down_{col}", help="下に移動"):
                                new_order = selected_in_order.copy()
                                new_order[i-1], new_order[i] = new_order[i], new_order[i-1]
                                unselected = [col for col in st.session_state.column_order 
                                            if col not in st.session_state.selected_columns]
                                st.session_state.column_order = new_order + unselected
                                st.rerun()
        
        # テンプレート保存（手動モードのみ）
        if st.session_state.mode == "manual" and st.session_state.selected_columns:
            with st.expander("💾 テンプレート保存", expanded=False):
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])
                with col1:
                    template_name = st.text_input("テンプレート名", placeholder="例: 月次売上レポート", key="template_name")
                    template_description = st.text_area("説明（任意）", placeholder="例: 毎月の売上データから必要な列を抽出", key="template_desc")
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("💾 テンプレート保存", type="secondary", key="save_template"):
                        if template_name:
                            config = {
                                'selected_columns': list(st.session_state.selected_columns),
                                'column_order': st.session_state.column_order,
                                'description': template_description,
                                'merge_operations': [],
                                'split_operations': [],
                                'empty_columns': []
                            }
                            save_template(template_name, config)
                            st.success(f"✅ テンプレート '{template_name}' を保存しました")
                        else:
                            st.error("❌ テンプレート名を入力してください")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 最終プレビューとダウンロード
        if st.session_state.selected_columns:
            st.markdown('<div class="section-header">📊 最終プレビュー・ダウンロード</div>', unsafe_allow_html=True)
            
            # 最終データフレーム作成
            selected_in_order = [col for col in st.session_state.column_order 
                               if col in st.session_state.selected_columns]
            
            final_columns = []
            for col in selected_in_order:
                if col in df.columns:
                    final_columns.append(col)
                else:
                    df[col] = ''
                    final_columns.append(col)
            
            final_df = df[final_columns].copy()
            
            # 統計情報表示
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #28a745; margin: 0;">{len(final_df):,}</h3>
                    <p style="margin: 0; color: #666;">出力行数</p>
                </div>
                ''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #28a745; margin: 0;">{len(final_columns)}</h3>
                    <p style="margin: 0; color: #666;">出力列数</p>
                </div>
                ''', unsafe_allow_html=True)
            with col3:
                reduction = round((1 - len(final_columns) / len(df.columns)) * 100, 1)
                st.markdown(f'''
                <div class="metric-card">
                    <h3 style="color: #17a2b8; margin: 0;">{reduction}%</h3>
                    <p style="margin: 0; color: #666;">列数削減率</p>
                </div>
                ''', unsafe_allow_html=True)
            with col4:
                # ダウンロードボタン
                try:
                    csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
                    original_name = uploaded_file.name.split('.')[0]
                    
                    st.download_button(
                        label="📥 CSV\nダウンロード",
                        data=csv_data,
                        file_name=f"processed_{original_name}.csv",
                        mime="text/csv",
                        type="primary",
                        key="download_btn",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ ダウンロード用データの準備でエラーが発生しました: {str(e)}")
            
            # プレビュー表示
            st.markdown('<div class="preview-table">', unsafe_allow_html=True)
            st.subheader(f"📋 最終データプレビュー")
            st.dataframe(final_df.head(15), use_container_width=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 列情報表示
            with st.expander("📋 選択された列の詳細", expanded=False):
                for i, col in enumerate(final_columns, 1):
                    unique_count = final_df[col].nunique()
                    null_count = final_df[col].isnull().sum()
                    st.write(f"**{i}. {col}** - ユニーク値: {unique_count:,}, 欠損値: {null_count:,}")
            
        else:
            st.markdown('<div class="section-header">⚠️ 列を選択してください</div>', unsafe_allow_html=True)
            st.info("出力するデータの列を選択してから、プレビューとダウンロードが可能になります。")
    
    # サイドバーにテンプレート管理
    with st.sidebar:
        if st.session_state.templates:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top: 0;">📚 保存済みテンプレート</h3>', unsafe_allow_html=True)
            
            for name, info in st.session_state.templates.items():
                with st.expander(f"📄 {name}", expanded=False):
                    st.markdown(f"**説明:** {info['description'] or 'なし'}")
                    st.markdown(f"**作成日:** {info['created_at']}")
                    st.markdown(f"**選択列数:** {len(info['config']['selected_columns'])}")
                    
                    if st.button("🗑️ 削除", key=f"delete_{name}", type="secondary", use_container_width=True):
                        del st.session_state.templates[name]
                        st.success(f"テンプレート '{name}' を削除しました")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 使用方法
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-top: 0;">📖 機能ガイド</h3>', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 主要機能
        - **⚡ テンプレート機能**  
          定型処理の自動化
        - **🔗 列結合**  
          複数列を1つにまとめる
        - **✂️ 列分割**  
          1列を複数に分割
        - **➕ 空列追加**  
          新しい空の列を追加
        - **🎯 列選択**  
          出力する列を選択
        - **🔄 順序調整**  
          列の並び順を変更
        
        ### 💡 Tips
        - エンコーディング自動判定
        - 重複列名の自動リネーム
        - テンプレート保存で作業効率化
        - リアルタイムプレビュー
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # フッター
    st.markdown('''
    <div style="text-align: center; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid #e8f4f8; color: #999;">
        <p>📊 <strong>CSV Organizer Pro</strong> - 高度なデータ整理ツール</p>
        <p><small>効率的なデータ処理でワークフローを改善</small></p>
    </div>
    ''', unsafe_allow_html=True)

# アプリケーション実行
if __name__ == "__main__":
    main()