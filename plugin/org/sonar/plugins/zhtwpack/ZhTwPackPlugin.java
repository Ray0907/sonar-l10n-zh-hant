package org.sonar.plugins.zhtwpack;

import java.util.Collections;
import org.sonar.api.Plugin;

public final class ZhTwPackPlugin implements Plugin {

	@Override
	public void define(Context context) {
		context.addExtensions(Collections.emptyList());
	}
}
